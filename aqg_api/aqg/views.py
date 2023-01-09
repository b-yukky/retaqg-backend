from django.shortcuts import render
from datetime import date
from django.http import Http404, response
from django.http import HttpResponse
from .models import * 
from .serializers  import *
from userauth.models import User
from django.contrib.auth.models import Group

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, DjangoModelPermissions
from .permissions import DjangoModelPermissionsWithRead
from .utils.model_creator import ModelCreator
from .mcq_selector import MCQSelector

from django.db import transaction
from .utils.models_init import init_models

# Create your views here.
DEV_DEBUG = False

ML_MODELS, DEFAULT_MODEL_NAME = init_models({
    'leafQad_base': True,
    'sumQd_base': False
}, DEV_DEBUG)

mcq_selector = MCQSelector(ML_MODELS)
model_creator = ModelCreator()

class ModelV2(APIView):
    
    permission_classes = [AllowAny]
    
    
    
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):

        if 'text' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST) 
        
        text = request.data['text']
        
        if 'model' in request.data:
            try:  
                model_name = Model.objects.get(name=request.data['model']).name
            except Model.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            model_name = DEFAULT_MODEL_NAME
        

        count = request.data['count'] if 'count' in request.data else 1
        topic = request.data['topic'] if 'topic' in request.data else ''
        dataset = request.data['dataset'] if 'dataset' in request.data else ''

        # mcq_generator.select_model(model_name)
        
        questions, answers, distractors = mcq_selector.generate_mcq_questions(text, model_name, count)
        
        if questions is False or questions == []:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        print(questions, answers)
        
        with transaction.atomic():
            questions = model_creator.add_mcq_to_db(questions, answers, distractors, text, model_name, topic, dataset)
        
        questions_serializer = QuestionDetailSerializer(questions, many=True)

        return Response(questions_serializer.data, status=status.HTTP_200_OK)


class ParagraphView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, *args):
        
        try:
            paragraphs = Paragraph.objects.all()
            paragraphs_serializer = ParagraphSerializer(paragraphs, many=True)
            return Response(paragraphs_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)


class QuestionView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, *args):
        try:
            questions = Question.objects.all()
            questions_serializer = QuestionSerializer(questions, many=True)
            return Response(questions_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class QuestionsDetailView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request, question_id, *args):
        try:
            question = Question.objects.get(id=question_id)
            question_serializer = QuestionDetailSerializer(question)
            return Response(question_serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class QuestionsByParagraphView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request, paragraph_id, *args):
        try:
            questions = Question.objects.filter(paragraph=paragraph_id)
            questions_serializer = QuestionDetailSerializer(questions, many=True)
            return Response(questions_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)

class EvaluationView(APIView):
    
    queryset = Evaluation.objects.all()
    permission_classes = [DjangoModelPermissionsWithRead]
    
    def get(self, request, question_id, *args):
        try:
            evaluation = Evaluation.objects.get(question=question_id, user=request.user)
            evaluation_serializer = EvaluationSerializer(evaluation)
            return Response(evaluation_serializer.data, status=status.HTTP_200_OK)
        except Evaluation.DoesNotExist:
            empty_evaluation_serializer = EvaluationSerializer(
                Evaluation(
                    question=Question.objects.get(id=question_id)
                )
            )
            return Response(empty_evaluation_serializer.data, status=status.HTTP_200_OK)
        except Evaluation.MultipleObjectsReturned:
            ''' This is not supposed to happen '''
            evaluation = Evaluation.objects.filter(question=question_id, user=request.user).first()
            evaluation_serializer = EvaluationSerializer(evaluation)
            return Response(evaluation_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, *args):
        evaluation_serializer = EvaluationSerializer(data=request.data)
        if evaluation_serializer.is_valid():
            evaluation_serializer.save(
                user=request.user
            )
            return Response(evaluation_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(evaluation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args):
        try:
            evaluation_id = request.data['id']
            evaluation = Evaluation.objects.get(id=evaluation_id)
        except Evaluation.DoesNotExist:
            evaluation = None
        evaluation_serializer = EvaluationSerializer(evaluation, data=request.data)
        if evaluation_serializer.is_valid():
            evaluation_serializer.save(
                user=request.user
            )
            return SelectQuestionToEvaluate.get(self, request)
        else:
            return Response(evaluation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, evaluation_id, *args):
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
        except Evaluation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SelectQuestionToEvaluate(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        queryset_question = Question.objects\
            .filter(status='EV')\
            .exclude(evaluations__user=request.user)\
            .order_by('paragraph')
        
        print(queryset_question)
        if queryset_question.count() > 0:
            question_serializer = QuestionDetailSerializer(queryset_question.first())
            return Response(question_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

class EvaluationStatisticsView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        completed = Question.objects.filter(status='EV', evaluations__user=request.user).count()
        remaining = Question.objects.filter(status='EV').exclude(evaluations__user=request.user).count()
        
        stats_serializer = EvaluationStatsSerializer({
            'questions_completed': completed,
            'questions_remaining': remaining
        })
        return Response(stats_serializer.data, status=status.HTTP_200_OK)

class ModelView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, *args):
        try:
            models = Model.objects.all()
            models_serializer = ModelSerializer(models, many=True)
            return Response(models_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DatasetView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, *args):
        try:
            datasets = Dataset.objects.all()
            datasets_serializer = DatasetSerializer(datasets, many=True)
            return Response(datasets_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class ProfileView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args):
        try:
            profile = Profile.objects.get(user=request.user)
            profile_serializer = ProfileSerializer(profile)
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            print(request.user.id)
            profile = Profile.objects.create(
                user=request.user
            )
        
        if 'english_proficiency' in request.data:
            group = Group.objects.get(name='en_verified')
            profile.user.groups.add(group)
            profile.save()
            
        profile_serializer = ProfileSerializer(profile, data=request.data)
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
