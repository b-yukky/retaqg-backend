
from xml.etree.ElementInclude import default_loader
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group
import uuid

# Create your models here.

class CustomManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password=None,**extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(password, **extra_fields)

    def create_subject_user(self):
        user = self.model()
        group_subject = Group.objects.get(name='subject')
        user.login_url = user.login_url + str(user.id)
        user.save(using=self._db)
        group_subject.user_set.add(user)
        return user

        


class User(AbstractUser):
    # Some rules adding username
    username_validator = UnicodeUsernameValidator()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email'), max_length=80, unique=True, null=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        null=True,
        blank=True # Same code that has django as a default only added this to say can be an empty value
    )
    
    login_url = models.URLField(max_length=200, default="https://la.ait.kyushu-u.ac.jp/qu/aqg/login/")
    #Custom Field
    # group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    objects = CustomManager()

    # Field for login
    USERNAME_FIELD = 'username'

    # Field for command createsuperuser
    REQUIRED_FIELDS = ['first_name','last_name']

    def __str__(self):
        return f"{self.id} - {self.username}"

