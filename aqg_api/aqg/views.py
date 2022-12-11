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
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .ml_models.mcq_generator import MCQGenerator
from .utils.model_creator import ModelCreator

from django.db import transaction
# Create your views here.

mcq_generator = None
mcq_generator = MCQGenerator()
model_creator = ModelCreator()


class ModelV2(APIView):
    
    
    DEFAULT_MODEL_NAME = 'SumQgQaQd_v2_base'
    
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):

        if not 'text'in request.data:
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

    
    def get(self, *args):
        
        try:
            paragraphs = Paragraph.objects.all()
            paragraphs_serializer = ParagraphSerializer(paragraphs, many=True)
            return Response(paragraphs_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)


class QuestionView(APIView):
    
    def get(self, *args):
        try:
            questions = Question.objects.all()
            questions_serializer = QuestionSerializer(questions, many=True)
            return Response(questions_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, *args):
        try:
            paragraph_id = request.data['paragraph_id']
            questions = Question.objects.filter(paragraph=paragraph_id)
            questions_serializer = QuestionDetailSerializer(questions, many=True)
            return Response(questions_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)

class EvaluationView(APIView):
    
    def get(self, *args):
        try:
            evaluations = Evaluation.objects.all()
            evaluations_serializer = EvaluationSerializer(evaluations, many=True)
            return Response(evaluations_serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, *args):
        evaluation_serializer = EvaluationSerializer(data=request.data)
        if evaluation_serializer.is_valid():
            evaluation_serializer.save()
            return Response(evaluation_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(evaluation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, evaluation_id, *args):
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
        except Evaluation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        evaluation_serializer = EvaluationSerializer(evaluation, data=request.data)
        if evaluation_serializer.is_valid():
            evaluation_serializer.save()
            return Response(evaluation_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(evaluation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, evaluation_id, *args):
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
        except Evaluation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
