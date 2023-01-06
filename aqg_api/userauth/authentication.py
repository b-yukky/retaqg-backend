from userauth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class AuthenticationWithoutPassword(ModelBackend):

    def authenticate(self, request, **kwargs):
        try:
            uuid = kwargs.get('uuid', None)
            if uuid is None:
                uuid = kwargs.get('username', None)
            user = User.objects.get(id=uuid)
            if user.groups.filter(name='subject').exists():
                return User.objects.get(id=uuid)
            else:
                raise exceptions.AuthenticationFailed("User does not belong to 'subject' group")
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(f'No user with uuid: {uuid}')

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class EmailBackend(ModelBackend):
    
    def authenticate(self, request, **kwargs):
        UserModel = get_user_model()
        try:
            email = kwargs.get('email', None)
            if email is None:
                email = kwargs.get('username', None)
            user = UserModel.objects.get(email=email)
            if user.check_password(kwargs.get('password', None)):
                return user
        except UserModel.DoesNotExist:
            return None
        return None
    