from ..models import *
from datetime import datetime
class ModelCreator():
    
    
    def __init__(self) -> None:
        ''' Empty initialization'''
        pass
    
    def add_mcq_to_db(self, questions: list, answers: list, distractors_list:list, context: str, model_name: str, topic_name: str, dataset: str):
        
        results = []
        
        try:
            model = Model.objects.get(name=model_name)
        except Model.DoesNotExist:
            model = None
        
        try:
            topic = Topic.objects.get(name=topic_name.lower())
        except Topic.DoesNotExist:
            topic = Topic(
                name=topic_name.lower()
            )
            topic.save()
        try:
            paragraph = Paragraph.objects.get(text=context)
        except Paragraph.DoesNotExist:
            paragraph = Paragraph(
                text=context,
                length=len(context),
                topic=topic,
                dataset=Dataset.objects.get(name=dataset)   
            )
            paragraph.save()
        
        for question_text, answer, distractors in zip(questions, answers, distractors_list):
            try:
                question = Question.objects.get(text=question_text, paragraph=paragraph, answer=answer, model=model)
            except Question.DoesNotExist:
                question = Question(
                    text=question_text,
                    answer=answer,
                    status='TE',
                    paragraph=paragraph,
                    model=model
                )
                question.save()

            results.append(question)
            for distractor in distractors:
                try:
                    distractor = Distractor.objects.get(text=distractor, question=question, model=model)
                except Distractor.DoesNotExist:
                    distractor = Distractor(
                        text=distractor,
                        question=question,
                        model=model
                    )
                    distractor.save()

        return results
        
        
    
