
import string
import pke
from pke.unsupervised import *
from pke import compute_document_frequency, compute_lda_model, load_document_frequency_file, load_lda_model
import fitz
from collections import defaultdict
import re
from pandas import read_csv

url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

def compute_df(doc, lang='en'):
    compute_document_frequency(
        documents=[doc],
        output_file="df-inspec.tsv.gz",
        language=lang,
        normalization='stemming',  
        n=5
    )
    df = load_document_frequency_file(input_file='df-inspec.tsv.gz')
    return df

def compute_lda(doc, stoplist, lang='en'):
    compute_lda_model(
        documents=[doc],
        output_file="lda-inspec.tsv.gz",
        n_topics=20,               
        language=lang,              
        stoplist=stoplist,
        normalization='stemming'    
    )
    lda = load_lda_model(input_file='lda-inspec.tsv.gz')
    return lda

def extract_keywords(text, algorithm, n=10):
    extractor = algorithm

    stoplist = list(string.punctuation)
    stoplist += pke.lang.stopwords.get('en')

    extractor.load_document(input=text, stoplist=stoplist)
    pos = {'NOUN', 'PROPN', 'ADJ'}
    
    if extractor.__class__.__name__ in ["TfIdf", "KPMiner"]:
        df = compute_df(text)
        extractor.grammar_selection(grammar="NP: {<ADJ>*<NOUN|PROPN>+}")
        extractor.candidate_weighting(df=df)
    elif extractor.__class__.__name__ in ["TopicalPageRank"]:
        lda = compute_lda(text, stoplist)
        extractor.candidate_weighting(lda_model=lda)
    else:
        extractor.grammar_selection(grammar="NP: {<ADJ>*<NOUN|PROPN>+}")
        extractor.candidate_weighting()
    
    keywords = [k for k,v in extractor.get_n_best(n=n)]
    
    return keywords


def extract_textblocks(file):
    pdf = fitz.open(file)
    
    textblocks = []

    for page in pdf:
        textblocks.append([p[4].strip().replace('\n',' ') for p in page.get_text('blocks') 
                           if p[6] == 0 and not re.search(url_regex, p[4])])

    pdf.close()
    return textblocks

def extract_paragraphs(page_textblocks, min_length=300, max_length=1500, divider=70):
    paragraph = ''
    paragraphs = defaultdict(list)
    for page_n, textblocks in enumerate(page_textblocks):
        for text in textblocks:
            if len(text) < divider:
                paragraphs[page_n].append("".join(paragraph.rstrip())) if len(paragraph) > min_length else None
                paragraph = ''
            else:
                paragraph += text + ' '
                if len(paragraph) > max_length:
                    paragraphs[page_n].append("".join(paragraph.rstrip()))
                    paragraph = ''
    
    return paragraphs

def process_paragraphs(pages, max_length=1500):
    
    def add_paragraph(l, paragraph):
        split_paragraph = paragraph.split('.')
        l.append(".".join(split_paragraph[:-1]) + '.')
        paragraph = split_paragraph[-1]
        return paragraph
    
    paragraphs = []
    paragraph = ''
    last_page = 0
    for n, page in list(pages.items()):
        for p in page:
            if n == last_page + 1:
                paragraph += p
                if len(paragraph) > max_length:
                    paragraph = add_paragraph(paragraphs, paragraph)
            else:
                paragraph = ''
                
        last_page = n
    
    return paragraphs

def select_paragraphs(paragraphs, best_keywords):
    keywords = defaultdict(list)

    for kw in best_keywords:
        for n_paragraph, paragraph in enumerate(paragraphs):
            if kw.lower() in paragraph.lower():
                keywords[kw].append(n_paragraph)

    keywords.keys()
    flatten = lambda lst: (item for sublist in lst for item in sublist)
    idx_paragraphs = list(set(flatten([ids for key, ids in keywords.items()])))
    selected_paragraphs = [p for i, p in enumerate(paragraphs) if i in idx_paragraphs]
    
    return selected_paragraphs

def process_pdf(file):
    
    page_textblocks = extract_textblocks(file)
    text = ' '.join([' '.join(p) for p in page_textblocks])

    page_paragraphs = extract_paragraphs(page_textblocks)
    paragraphs = process_paragraphs(page_paragraphs)
    best_keywords = extract_keywords(text, KPMiner(), n=10)
    
    selected_paragraphs = select_paragraphs(paragraphs, best_keywords)
    
    return selected_paragraphs

def process_csv(file):
    
    df = read_csv(file, sep=',', lineterminator='\n', encoding='utf-8')
    return df['text'], df['theme\r']
