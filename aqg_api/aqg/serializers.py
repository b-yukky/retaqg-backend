from rest_framework import serializers
from .models import *
from userauth.models import User, Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source='id')
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
        
class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
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
        depth = 2
        
    def to_representation(self, instance):
        question = super().to_representation(instance)
        question["status"] = instance.get_status_display()
        return question
        
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

        
class ProfileSerializer(serializers.ModelSerializer):
    
    max_questions = serializers.IntegerField(required=False)
    completed_questions = serializers.IntegerField(required=False)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    groups = GroupSerializer(source='user.groups', many=True, read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user', 'user_detail', 'max_questions', 'completed_questions']

class ExperimentSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentSetting
        fields = '__all__'
        
class EvaluationStatsSerializer(serializers.Serializer):
    
    questions_completed = serializers.IntegerField()
    questions_remaining = serializers.IntegerField()

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
