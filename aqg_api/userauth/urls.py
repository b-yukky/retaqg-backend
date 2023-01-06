from django.urls import include, path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
)
from .views import GenerateSubjectAccountView, MyTokenObtainPairView, TokenObtainPairWithoutPasswordView

urlpatterns = [
    path('login/', MyTokenObtainPairView.as_view()),
    path('login/nopassword/', TokenObtainPairWithoutPasswordView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create-subject/', GenerateSubjectAccountView.as_view()),
]
