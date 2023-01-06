from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from aqg.serializers  import UserSerializer

from userauth.models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['groups'] = self.user.groups.values_list('name', flat=True)
        return data


class TokenObtainPairWithoutPasswordSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

    def validate(self, attrs):
        attrs.update({'password': ''})
        data = super(TokenObtainPairWithoutPasswordSerializer, self).validate(attrs)
        data['uuid'] = self.user.id
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class TokenObtainPairWithoutPasswordView(TokenObtainPairView):
    serializer_class = TokenObtainPairWithoutPasswordSerializer


class GenerateSubjectAccountView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        user = User.objects.create_subject_user()
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

