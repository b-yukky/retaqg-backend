from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STATUS = [
    ('TE', 'TEST'),
    ('EV', 'EVALUATION'),
    ('PR', 'PRODUCTION'),
]

class Paragraph(models.Model):
    
    length = models.IntegerField()
    text = models.TextField(blank=False, null=True)
    
    document_name = models.CharField(max_length=120, blank=True)
    topic = models.CharField(max_length=80, blank=True)
    summary = models.TextField(blank=True)
    
    def __str__(self)  -> str:
        sumup = self.summary[:100] if len(self.summary) > 0 else self.text[:30]
        return f"{self.id} - {sumup}"

class Model(models.Model):
    
    name = models.CharField(max_length=40, unique=True)
    
    creation_date = models.DateTimeField(auto_created=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name

class Question(models.Model):
    
    text = models.CharField(max_length=180)
    answer = models.CharField(max_length=180)
    timestamp = models.DateTimeField(auto_now=True)
    
    status = models.CharField(choices=STATUS, default='TS', max_length=2)
    
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, null=True)
    
    def __str__(self) -> str:
        return f"{self.id} - {self.text}"
    
class Evaluation(models.Model):
    
    relevance = models.IntegerField(default=0)
    acceptability = models.BooleanField(default=False)
    difficulty = models.IntegerField(default=0)
    choices = models.IntegerField(default=0)

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='evaluations')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='evaluations')
    
    def __str__(self) -> str:
        return f"{self.question} - {self.id}"
    
class Distractor(models.Model):
    
    text = models.CharField(max_length=180)
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='distractors')
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, related_name='distractors', null=True)

    def __str__(self) -> str:
        return self.text

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    english_validation = models.BooleanField(default=False)
    english_false_answers = models.IntegerField(default=0)
    english_proficiency = models.IntegerField(default=0)
    is_student = models.BooleanField(default=False)
