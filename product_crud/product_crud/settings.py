import pymysql
pymysql.install_as_MySQLdb()

import os
import environ
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# Security
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Installed apps
INSTALLED_APPS = [
    'product.apps.ProductConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'product_crud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'product.context_processors.cart_count',
                'product.context_processors.wishlist_count',
                'product.context_processors.review_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'product_crud.wsgi.application'

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='3306'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication & Email settings
LOGOUT_REDIRECT_URL = 'welcome'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/product/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Twilio API settings
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER')

# Google Authentication
SOCIAL_AUTH_GOOGLE_CLIENT_ID = env('SOCIAL_AUTH_GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_SECRET = env('SOCIAL_AUTH_GOOGLE_SECRET')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'APP': {
            'client_id': SOCIAL_AUTH_GOOGLE_CLIENT_ID,
            'secret': SOCIAL_AUTH_GOOGLE_SECRET,
        },
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}



AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default backend
    # 'allauth.account.auth_backends.AuthenticationBackend',
)


SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE' : [
            'profile',
            'email'
        ],
        'APP': {
            'client_id': SOCIAL_AUTH_GOOGLE_CLIENT_ID,
            'secret': SOCIAL_AUTH_GOOGLE_SECRET,
        },
        'AUTH_PARAMS': {
            'access_type':'online',
        }
    }
}


# settings.py

STATIC_URL = '/static/'

# Directory for serving static files (during development)
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Point to the static directory in your project
]

# Static files will be stored here during deployment
STATIC_ROOT = BASE_DIR / "staticfiles"  # Only for production (using collectstatic)
