import torch
import matplotlib.pyplot as plt

from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from transformers import BartTokenizer, BartForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForQuestionAnswering

from transformers import pipeline as transformer_pipeline
from .distractors_generation.race_t5small import DistractorGenerator

from ..utils.duplicate_removal import remove_duplicates, remove_distractors_duplicate_with_correct_answer
from ..utils.text_cleaning import clean_text
from ..utils import text_processing as text_processing
import sense2vec as s2v
from sense2vec import Sense2Vec

from pke.unsupervised import *
from flashtext import KeywordProcessor

import nltk
import pytorch_lightning as pl
import time

from nltk.translate.bleu_score import sentence_bleu

    
class SumBaseMCQGenerator():
    
    def __init__(self, hyperparameters: dict={}):
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu') 
            print('Device on:', self.device)
            self.hyperparameters = self._init_hyperparameters(hyperparameters)
            
            start_time = time.perf_counter()
            print('Loading ML Models...')
        
            self.summarization_model = AutoModelForSeq2SeqLM.from_pretrained(self.hyperparameters['summarization_model'], cache_dir='weights/').to(self.device)
            self.summarization_tokenizer = AutoTokenizer.from_pretrained(self.hyperparameters['summarization_model'], cache_dir='weights/')
            print('Loaded Summarization in', round(time.perf_counter() - start_time, 2), 'seconds.')
            self.question_model = T5ForConditionalGeneration.from_pretrained(self.hyperparameters['question_model'], cache_dir='weights/').to(self.device)
            self.question_tokenizer = T5Tokenizer.from_pretrained(self.hyperparameters['question_model'], cache_dir='weights/')
            print('Loaded Question generation in', round(time.perf_counter() - start_time, 2), 'seconds.')
            self.qa_model = AutoModelForQuestionAnswering.from_pretrained(self.hyperparameters['qa_model'], cache_dir='weights/')
            self.qa_tokenizer = AutoTokenizer.from_pretrained(self.hyperparameters['qa_model'], cache_dir='weights/')
            self.qa_pipeline = transformer_pipeline('question-answering', model=self.qa_model, tokenizer=self.qa_tokenizer)
            print('Loaded question answering in', round(time.perf_counter() - start_time, 2), 'seconds.')
            self.distractor_model= DistractorGenerator()
            self.s2v = Sense2Vec().from_disk('weights/s2v_old')
            print('Loaded Distractor generation in', round(time.perf_counter() - start_time, 2), 'seconds.')
            
            
    def generate_mcq_questions(self, input_text, desired_count):
        context = clean_text(input_text)
        summary = self._summarize(context)
        
        answers = self._get_cross_keywords(context, summary, self.hyperparameters['keyword_algorithm'], desired_count)
        questions = []
        distractors = []
        for answer in answers:
            question = self._get_question(context, answer)
            score, pred = self._evaluate_question(question, answer, context)
            if score > 0.5:
                questions.append(question) 
                false_answers = remove_duplicates(self.distractor_model.generate(5, answer, question, input_text))
                false_answers = remove_distractors_duplicate_with_correct_answer(answer, false_answers)
                distractors.append(false_answers)
        return questions, answers, distractors
    
    def _init_hyperparameters(self, hyperparameters):
        if not hyperparameters:
            hyperparameters = {
                'summarization_model': 'sshleifer/distilbart-cnn-12-6',
                'question_model': 'mrm8488/t5-base-finetuned-question-generation-ap',
                'qa_model': 'deepset/roberta-base-squad2',
                'keyword_algorithm': TextRank()
            }
        return hyperparameters

    def _summarize(self, input_text):
        tokenized_text = self.summarization_tokenizer.encode(input_text, return_tensors='pt', max_length=1024, truncation=True).to(self.device)
        summary_ids = self.summarization_model.generate(tokenized_text, num_beams=5, min_length=10, max_length=50)
        summary = self.summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    
    def _get_cross_keywords(self, originaltext, summarytext, algorithm=TextRank(), n=3):
        keyword_processor = KeywordProcessor()
        keywords = text_processing.extract_keywords(originaltext, algorithm, n=10)

        print('Keywords extracted:', keywords)
        print('Summary:', summarytext)

        for keyword in keywords:
            keyword_processor.add_keyword(keyword)
        
        keywords_found = keyword_processor.extract_keywords(summarytext)
        keywords_found = list(set(keywords_found))

        best_keywords = []
        for keyword in keywords:
            if keyword in keywords_found:
                best_keywords.append(keyword)

        return best_keywords[:n]
    
    def _get_question(self, context, answer):
        input_text = "answer: %s context: %s </s>" % (answer, context)
        features = self.question_tokenizer([input_text], return_tensors='pt', max_length=1024, truncation=True).to(self.device)
        
        output = self.question_model.generate(input_ids=features['input_ids'], 
               attention_mask=features['attention_mask'],
               num_beams=5,
               max_length=72)
        dec = self.question_tokenizer.decode(output[0], skip_special_tokens=True)
        
        Question = dec.replace("question:", "")
        Question = Question.strip()
        
        return Question
    
    def _evaluate_question(self, question, answer, context):
        qa_input = {'question': question, 'context':  context}
        res = self.qa_pipeline(qa_input)
        pred = res['answer'].replace('\n', '').lower().split(' ')
        print(f"pred {pred}: answer {answer}")
        score = sentence_bleu([answer.lower().split(' ')], pred, weights=[1])
        print('score', score)
        return score, " ".join(pred)
    
    def _remove_questions(self, context, questions, answers, qa_pipeline, threshold=0.5):
        keep_questions = []
        keep_answers = []
        for q, a in zip(questions, answers):
            score, _ = self.evaluate_question(q, a, context, qa_pipeline)
            if score > threshold:
                keep_questions.append(q)
                keep_answers.append(a)
        
        return keep_questions, keep_answers

    def _get_s2v_distractors(self, answer):
        distractors =[]
        try:
            distractors = s2v.sense2vec_get_words(answer, self.s2v_model)
            if len(distractors) > 0:
                print(" Sense2vec_distractors successful for word : ", answer)
                return distractors,"sense2vec"
        except Exception:
            print (" Sense2vec_distractors failed for word : ",answer)
            
        return distractors, "None"

    def _generate_distractors(self, context: str, question, answer):
        distractors = self.distractor_model.generate(3, answer, question, context)
        
        return distractors
