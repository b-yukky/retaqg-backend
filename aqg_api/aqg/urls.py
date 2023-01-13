from django.urls import include, path, re_path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)

router.register(r'experiment/settings', views.ExperimentSettingViewSet, basename='experiment-settings')

urlpatterns = [
    
    path('question/generate/v2/', views.ModelV2.as_view()),
    path('evaluation/', views.EvaluationView.as_view()),
    path('evaluation/<int:question_id>', views.EvaluationView.as_view()),
    path('evaluation/question/<int:question_id>', views.EvaluationView.as_view()),
    path('question/evaluation/select/', views.SelectQuestionToEvaluate.as_view()),
    path('question/list/', views.QuestionView.as_view()),
    path('question/detail/<int:question_id>', views.QuestionsDetailView.as_view()),
    path('question/detail/paragraph/<int:paragraph_id>', views.QuestionsByParagraphView.as_view()),
    path('paragraph/list/', views.ParagraphView.as_view()),
    path('evaluation/stats/', views.EvaluationStatisticsView.as_view()),
    path('model/list/', views.ModelView.as_view()),
    path('dataset/list/', views.DatasetView.as_view()),
    path('my-profile/', views.ProfileView.as_view()),
    path('my-profile/add-questions/', views.AddQuestionsView.as_view()),
    path('my-profile/add-questions/<int:n>', views.AddQuestionsView.as_view()),
    path('experiment/settings/active/', views.ActiveExperimentSettingView.as_view()),
    path('experiment/settings/active/change/<int:setting_id>', views.ActiveExperimentSettingView.as_view()),
    path('experiment/settings/active/change/<int:setting_id>', views.ActiveExperimentSettingView.as_view()),
    path('experiment/subjects/info/', views.SubjectsInfoView.as_view()),
    path('', include(router.urls))

]

