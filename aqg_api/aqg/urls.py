from django.urls import include, path, re_path
from . import views

urlpatterns = [
    
    path('question/generate/v2/', views.ModelV2.as_view()),
    path('evaluation/', views.EvaluationView.as_view()),
    path('evaluation/<int:evaluation_id>', views.EvaluationView.as_view()),
    path('evaluation/question/<int:question_id>', views.EvaluationView.as_view()),
    path('question/evaluation/select/', views.SelectQuestionToEvaluate.as_view()),
    path('question/list/', views.QuestionView.as_view()),
    path('question/detail/<int:question_id>', views.QuestionsDetailView.as_view()),
    path('question/detail/paragraph/<int:paragraph_id>', views.QuestionsByParagraphView.as_view()),
    path('paragraph/list/', views.ParagraphView.as_view()),
    path('evaluation/stats/', views.EvaluationStatisticsView.as_view()),
    path('model/list/', views.ModelView.as_view()),
]
