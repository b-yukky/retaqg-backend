from ..models import *
from datetime import datetime
class ModelCreator():
    
    
    def __init__(self) -> None:
        pass
    
    def add_mcq_to_db(self, questions: list, answers: list, distractors_list:list, context: str, model_name: str):
        
        results = []
        
        try:
            model = Model.objects.get(name=model_name)
        except Model.DoesNotExist:
            model = None
        
        paragraph = Paragraph(
            text=context,
            length=len(context)        
        )
        paragraph.save()
        
        
        
        for question_text, answer, distractors in zip(questions, answers, distractors_list):
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
                distractor = Distractor(
                    text=distractor,
                    question=question,
                    model=model
                )
                distractor.save()
        
        return results
        
        
    
