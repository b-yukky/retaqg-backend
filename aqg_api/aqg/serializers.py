from rest_framework import serializers
from .models import *
from userauth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = '__all__'
        
class DistractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distractor
        fields = '__all__'  

class DistractorMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distractor
        fields = ['text'] 

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    
    distractors = DistractorMinSerializer(many=True, read_only=True)
    model = serializers.SlugRelatedField(slug_field='name', queryset=Model.objects.all())
    
    class Meta:
        model = Question
        fields = '__all__'
        
    def to_representation(self, instance):
        question = super().to_representation(instance)
        question["status"] = instance.get_status_display()
        return question
        
class QuestionDetailSerializer(serializers.ModelSerializer):
    
    distractors = DistractorMinSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'
        depth = 1
        
    def to_representation(self, instance):
        question = super().to_representation(instance)
        question["status"] = instance.get_status_display()
        return question
        
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

        
class ProfileSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Profile
        exclude = ['user']

class EvaluationStatsSerializer(serializers.Serializer):
    
    questions_completed = serializers.IntegerField()
    questions_remaining = serializers.IntegerField()
    