"""
Django settings for carlease project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Add your production hosts (e.g., for Heroku or your custom domain)
if not DEBUG:
    ALLOWED_HOSTS = ['carlease.onrender.com']
else:
    ALLOWED_HOSTS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'clients',
    'Customers',
    'Admins'
]

MIDDLEWARE = [
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'carlease.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('Templates'))],
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

WSGI_APPLICATION = 'carlease.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Replace the SQLite DATABASES configuration with PostgreSQL:
DATABASES = {
    'default': dj_database_url.config(
        # Replace this value with your local database's connection string.
        default='postgresql://carlease:ira2n9UVrRK0mFE8aIWnd5EtEUUeOP3I@dpg-ct9m7i5umphs73fc483g-a.oregon-postgres.render.com/carlease',
        conn_max_age=600
    )
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STRIPE_TEST_PUBLIC_KEY = 'your-stripe-public-key'
STRIPE_TEST_SECRET_KEY = 'your-stripe-secret-key'
STRIPE_WEBHOOK_SECRET = 'your-webhook-signing-secret'
STRIPE_SECRET_KEY = ''

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # TLS port for Gmail
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'oesigbone@gmail.com'  # Replace with your Gmail email address
EMAIL_HOST_PASSWORD = 'mgtj dweb qvqb zsgf'  # Replace with your Gmail password or app-specific password

# This production code might break development mode, so we check whether we're in DEBUG mode
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# This is where the static files will be collected for production (Render or any other cloud service)
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Make sure this path exists

    # Enable WhiteNoise to handle static files for production
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Directories where Django will search for additional static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Ensure that this directory contains your static files during development
]



MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_SSL_REDIRECT = False



if DEBUG:
    CACHE_MIDDLEWARE_SECONDS = 0  # Disable caching in development
    CACHE_MIDDLEWARE_ALIAS = 'default'  # Ensure cache is cleared every time
else:
    CACHE_MIDDLEWARE_SECONDS = 300  # Enable caching in production
    CACHE_MIDDLEWARE_ALIAS = 'default'  # Use default cache alias

    # # You can define your cache backend for production (e.g., Redis, Memcached)
    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django_redis.cache.RedisCache',
    #         'LOCATION': 'redis://127.0.0.1:6379/1',  # Your Redis server address and database number
    #     }
    # }


