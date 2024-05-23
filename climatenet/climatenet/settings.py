import os
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = ['climatenet.am', 'dev.climatenet.am', "https://dev.climatenet.am", 'localhost']

APPEND_SLASH = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'aws': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '5432',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'backend',
    'corsheaders',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'climatenet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR.parent.parent,  'frontend', 'build')],
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


WSGI_APPLICATION = 'climatenet.wsgi.application'

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR,  'static')

STATICFILES_DIRS = [
    BASE_DIR.parent.parent / "frontend/build/static"
]

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('hy', _('Armenian')),
]

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
   os.path.join(BASE_DIR, 'locale')
]

CORS_ORIGIN_WHITELIST = [
    "http://localhost:8000",
    "http://climatenet.am",
    "https://dev.climatenet.am",
    "http://dev.climatenet.am",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "https://dev.climatenet.am",
    "http://dev.climatenet.am",
]
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_SITE_TITLE = "ClimateNet Admin"
ADMIN_SITE_HEADER = "ClimateNet Administration"