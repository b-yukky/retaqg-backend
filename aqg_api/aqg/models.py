from django.db import models
from userauth.models import User

# Create your models here.
STATUS = [
    ('TE', 'TEST'),
    ('EV', 'EVALUATION'),
    ('PR', 'PRODUCTION'),
]

class Dataset(models.Model):
    
    name = models.CharField(max_length=40, unique=True)
    
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return f"{self.id} - {self.name}"

class Topic(models.Model):
    
    name = models.CharField(max_length=100, unique=True)
    
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return f"{self.name}"

class Paragraph(models.Model):
    
    length = models.IntegerField()
    text = models.TextField(blank=False, null=True)
    
    document_name = models.CharField(max_length=120, blank=True)
    topic_old = models.CharField(max_length=80, blank=True)
    summary = models.TextField(blank=True)
    
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, related_name='paragraphs')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name='paragraphs')

    def __str__(self)  -> str:
        sumup = self.summary[:100] if len(self.summary) > 0 else self.text[:30]
        return f"{self.id} - {sumup}"

class Model(models.Model):
    
    name = models.CharField(max_length=40, unique=True)
    
    active = models.BooleanField(default=True)
    
    creation_date = models.DateTimeField(auto_created=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name

class Question(models.Model):
    
    text = models.CharField(max_length=500)
    answer = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now=True)
    
    status = models.CharField(choices=STATUS, default='TS', max_length=2)
    
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE, related_name='questions')
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, null=True)
    
    def __str__(self) -> str:
        return f"{self.id} - {self.text}"

    
class Evaluation(models.Model):
    
    relevance = models.IntegerField(default=0)
    acceptability = models.BooleanField(default=False)
    difficulty = models.IntegerField(default=0)
    choices = models.IntegerField(default=0)
    confidence = models.IntegerField(default=0)

    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(auto_now=True, null=True)
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='evaluations')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='evaluations')
    
    def __str__(self) -> str:
        return f"{self.question} - {self.id}"
    
class Distractor(models.Model):
    
    text = models.CharField(max_length=500)
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='distractors')
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, related_name='distractors', null=True)

    def __str__(self) -> str:
        return self.text

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    english_proficiency = models.IntegerField(default=0)
    additional_questions = models.IntegerField(default=0)
    topic_preferences = models.JSONField(default=dict)
    
    def __str__(self) -> str:
        return f"profile - {self.user}"

class ExperimentSetting(models.Model):
    
    name = models.CharField(max_length=40, unique=True)
    
    max_eval_per_question = models.IntegerField(default=5)
    max_questions_per_subject = models.IntegerField(default=20)
    
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.name}"

