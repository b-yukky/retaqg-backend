"""
Django settings for aqg_api project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
from telnetlib import AUTHENTICATION
from sshtunnel import SSHTunnelForwarder

from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-2o(5!9+na6d(+n#$lwi&n_r@@#384m01$v_cr6*@q833gp^4$9"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DJANGO_DEBUG", default=0))
PROD_DEBUG = int(os.environ.get("PROD_DEBUG", default=0))
PRODUCTION = int(os.environ.get("PRODUCTION", default=0))

SERVER_IP = '133.5.19.111'
PATH_TO_SSH_PRIVATE_KEY = "C:\\Users\\LIMU\\.ssh\\id_ed25519"
SSH_USERNAME = 'ladev'
LOCAL_DB_PORT_ON_THE_SERVER = 3306

if not PRODUCTION or PROD_DEBUG:
    ssh_tunnel = SSHTunnelForwarder(
        SERVER_IP,
        ssh_private_key=PATH_TO_SSH_PRIVATE_KEY,
        ssh_username=SSH_USERNAME,
        remote_bind_address=('192.168.100.65', LOCAL_DB_PORT_ON_THE_SERVER),
    )
    ssh_tunnel.start()

try:
    ssh_tunnel_port = ssh_tunnel.local_bind_port
except Exception:
    ssh_tunnel_port = 3306

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    'rest_framework_simplejwt',
    "corsheaders",
    "aqg.apps.AqgConfig",
    "userauth.apps.UserauthConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = "aqg_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "aqg_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


CORS_ORIGIN_ALLOW_ALL = True

if PRODUCTION:
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get("DATABASE_PROD_NAME"),
            'HOST': os.environ.get("DATABASE_PROD_HOST"),
            'PORT': os.environ.get("DATABASE_PROD_PORT", default=ssh_tunnel_port),
            'USER': os.environ.get("DATABASE_PROD_USERNAME"),
            'PASSWORD': os.environ.get("DATABASE_PROD_PASSWORD")  
        }
    }
    
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = ['https://la.ait.kyushu-u.ac.jp', 'https://la.ait.kyushu-u.ac.jp/', 'https://la.ait.kyushu-u.ac.jp/qu/aqg/']
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    
    FORCE_SCRIPT_NAME = '/qu/aqg/api/'
    
    
    
    # SECURE_BROWSER_XSS_FILTER = True
    # SECURE_SSL_REDIRECT = True
    
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": os.environ.get("DATABASE_DEV_HOST"),
            "PORT": os.environ.get("DATABASE_DEV_PORT", default=ssh_tunnel_port),
            "NAME": os.environ.get("DATABASE_DEV_NAME"),
            "USER": os.environ.get("DATABASE_DEV_USERNAME"),
            "PASSWORD": os.environ.get("DATABASE_DEV_PASSWORD"),
        }
    }

AUTHENTICATION_BACKENDS = {
    'userauth.authentication.EmailBackend',
    'userauth.authentication.AuthenticationWithoutPassword',
    'django.contrib.auth.backends.ModelBackend',
}


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'NON_FIELD_ERRORS_KEY': 'global',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/minute',
        'user': '300/minute'
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = 'userauth.User'


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/' if not PRODUCTION else '/qu/aqg/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/' if not PRODUCTION else '/qu/aqg/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
