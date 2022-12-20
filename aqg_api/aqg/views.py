from django.shortcuts import render
from datetime import date
from django.http import Http404, response
from django.http import HttpResponse
from .models import * 
from .serializers  import *
from django.contrib.auth.models import User
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .ml_models.mcq_generator import MCQGenerator
from .utils.model_creator import ModelCreator

from django.db import transaction
# Create your views here.

mcq_generator = None
# mcq_generator = MCQGenerator()
model_creator = ModelCreator()


class ModelV2(APIView):
    
    permission_classes = [AllowAny]
    
    DEFAULT_MODEL_NAME = 'SumQgQaQd_v2_base'
    
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):

        if 'text' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST) 
        
        text = request.data['text']
        
        if 'model' in request.data:
            try:  
                model_name = Model.objects.get(model_name=request.data['model']).model_name
            except Model.DoesNotExist:
                model_name = self.DEFAULT_MODEL_NAME
        else:
            model_name = self.DEFAULT_MODEL_NAME
        
        
        # mcq_generator.select_model(model_name)
        
        questions, answers, distractors = mcq_generator.generate(text)
        
        with transaction.atomic():
            questions = model_creator.add_mcq_to_db(questions, answers, distractors, text, model_name)
        
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
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, question_id, *args):
        try:
            evaluation = Evaluation.objects.get(question=question_id, user__username=request.user)
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
            evaluation = Evaluation.objects.filter(question=question_id, user__username=request.user).first()
            evaluation_serializer = EvaluationSerializer(evaluation)
            return Response(evaluation_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, *args):
        evaluation_serializer = EvaluationSerializer(data=request.data)
        if evaluation_serializer.is_valid():
            evaluation_serializer.save(
                user=User.objects.get(username=request.user)
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
                user=User.objects.get(username=request.user)
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
            .exclude(evaluations__user__username=request.user)\
            .order_by('paragraph')
        
        print(queryset_question)
        if queryset_question.count() > 0:
            question_serializer = QuestionDetailSerializer(queryset_question.first())
            return Response(question_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
