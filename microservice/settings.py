"""
Django settings for microservice project.
Generated by 'django-admin startproject' using Django 3.1.7.
For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import logging.config

from pathlib import Path
from environs import Env


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# #############################################################################
# ######################## Sensitive Section ##################################
# #############################################################################
env = Env()
env.read_env(recurse=True)

# Determine the Environment
ENVIRONMENT = env.str("ENVIRONMENT", "PROD")
IS_LOCAL = env.bool("IS_LOCAL", False)
DEBUG = env.bool("DEBUG", False)

# Security Variable
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", False)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", False)
SECURE_BROWSER_XSS_FILTER = env.bool("SECURE_BROWSER_XSS_FILTER", True)

# set hosts
ALLOWED_HOSTS = env.list("PROD_ALLOWED_HOSTS")
if ENVIRONMENT == "DEV":
    ALLOWED_HOSTS += env.list("DEV_ALLOWED_HOSTS")


# Application definition
LOCAL_INSTALLED_APPS = [
    "apis",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party apps
    "corsheaders",
    "rest_framework",
    "django_extensions",
] + LOCAL_INSTALLED_APPS

MIDDLEWARE = [
    # 3rd party middleware
    "corsheaders.middleware.CorsMiddleware",
    # Built-in middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "microservice.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates/")
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            }
        },
    },
]

WSGI_APPLICATION = "microservice.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("DB_DATABASE"),
        "USER": env.str("DB_USERNAME"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.str("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Log settings
# https://docs.djangoproject.com/en/2.2/topics/logging/
LOG_FORMAT = os.getenv("LOG_FORMAT", f"%(asctime)s:{logging.BASIC_FORMAT}")

LOG_LEVEL = env.int("LOG_LEVEL", logging.DEBUG)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": LOG_FORMAT,
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "apps": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}