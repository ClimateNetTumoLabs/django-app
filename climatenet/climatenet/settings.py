import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

print(f'BASE_DIR {BASE_DIR}')

DEBUG = False

SECRET_KEY = 'django-insecure-h28n+_l2r%&+cj!)syu9@7l5juruacb*7_uoye4ba0n*sb&oo6'

ALLOWED_HOSTS = ['climatenet.am', 'dev.climatenet.am', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'climatenet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,  'frontend', 'build')],
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

print(f'Taplates {TEMPLATES[0]["DIRS"]}')

WSGI_APPLICATION = 'climatenet.wsgi.application'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,  'static')

STATICFILES_DIRS = [
    BASE_DIR.parent.parent / "frontend/build/static"
]

print(f'Static root  {STATIC_ROOT}')

CORS_ORIGIN_WHITELIST = [
    "https://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://climatenet.am",
    "https://climatennet.am"
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

# Configure the logger
logger = logging.getLogger('backend.views')
logger.setLevel(logging.DEBUG)

# Create a file handler for the log file
log_file = 'debug.log'
file_handler = logging.FileHandler(log_file)

# Create a formatter for the log entries
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'backend': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
