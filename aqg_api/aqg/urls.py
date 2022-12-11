from django.urls import include, path, re_path
from . import views

urlpatterns = [
    
    path('question/generate/v2/', views.ModelV2.as_view()),
    path('question/evaluation/', views.EvaluationView.as_view()),
    path('question/list/', views.QuestionView.as_view()),
    path('paragraph/list/', views.ParagraphView.as_view())
]
