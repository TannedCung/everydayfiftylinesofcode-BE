"""
Django settings for daily50 project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = env('DJANGO_SECRET_KEY', default='your-default-secret-key')  # Use default for development
DEBUG = env.bool('DJANGO_DEBUG', default=True)  # Convert to boolean

ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

# Allow all origins (for development purposes only, not recommended in production)
# CORS_ALLOW_ALL_ORIGINS = True

# Additional settings (optional)
# Allow cookies to be sent with cross-origin requests
CORS_ALLOW_CREDENTIALS = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',      # Required by allauth

    # allauth for authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'rest_framework',
    "rest_framework.authtoken",
    "dj_rest_auth",
    'dj_rest_auth.registration',
    "oauth2_provider",
    'drf_spectacular',
    "drf_spectacular_sidecar",  # Optional, for better UI assets
    'corsheaders',
    'storages',
    'django_filters',

    'core'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

ROOT_URLCONF = 'daily50.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'daily50.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# settings.py
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

REST_USE_JWT = True

SITE_ID = 1

# URL where users will be redirected after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

GITHUB_CALLBACK = env('GITHUB_CALLBACK', default='http://localhost:19981/accounts/github/login/callback/')

SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': env('SOCIAL_AUTH_GITHUB_KEY'),
            'secret': env('SOCIAL_AUTH_GITHUB_SECRET'),
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Documentation',
    'DESCRIPTION': 'Your API description here.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY_DEFINITIONS': {
        'Bearer Token': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        },
    },
    'SECURITY': [{'Bearer Token': []}],
}
# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Minio settings
AWS_ACCESS_KEY_ID = env('ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = env('S3_ENDPOINT_URL')
AWS_S3_USE_SSL = env.bool('S3_USE_SSL', default=False)
AWS_QUERYSTRING_AUTH = env.bool('QUERYSTRING_AUTH', default=True)
AWS_DEFAULT_ACL = env('DEFAULT_ACL', default=None)

# Celery settings
CELERY_TIMEZONE = "Asia/Ho_Chi_Minh"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'