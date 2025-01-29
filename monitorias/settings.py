"""
Django settings for monitorias project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os

import dj_database_url

import rollbar  # pylint: disable=W0611


import cloudinary_storage  # pylint: disable=W0611


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

ALLOWED_HOSTS = []

if os.getenv("DJANGO_ENVIRONMENT") == "PRODUCTION":
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    DEBUG = os.getenv("DEBUG")
    print(os.getenv("DJANGO_ENVIROMENT"))
    print(DEBUG)
    ALLOWED_HOSTS.append(os.getenv("DJANGO_HOSTS"))
    DATABASES = {
        "default": dj_database_url.config(
            # pylint: disable=C0301
            default=os.getenv("DB_URL"),
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = ("django-insecure-v8pebn^$2l9p&b8n^h(sk8*_28e(n_2q5#*znxf-3l9*egn!xu",)

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS.append("127.0.0.1")

    # Database
    # https://docs.djangoproject.com/en/4.0/ref/settings/#databases
    # pylint: disable=C0301

    # DATABASES = {"default": dj_database_url.config(default=os.getenv("DB_URL"))}

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR + "db.sqlite3",
        }
    }

# Application definition

INSTALLED_APPS = [
    "fixtures",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "accounts",
    "core",
    "django_filters",
    "drf_spectacular",
    "forum_amo",
    "cloudinary",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "rollbar.contrib.django.middleware.RollbarNotifierMiddleware",
]

ROOT_URLCONF = "monitorias.urls"

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

WSGI_APPLICATION = "monitorias.wsgi.application"

# User models
AUTH_USER_MODEL = "accounts.CustomUser"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []

# Email (smtp-backend)
# https://docs.djangoproject.com/en/4.0/topics/email/#smtp-backend

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Fortaleza"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
MEDIA_ROOT = "imagens"
MEDIA_URL = "/"
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

FIXTURE_DIRS = ["fixtures"]

# https://docs.rollbar.com/docs
ROLLBAR = {
    "access_token": "cd05d027472f40898ca9021789476e39",
    "environment": "development" if DEBUG else "production",
    "root": BASE_DIR,
    "suppress_reinit_warning": True,
    "enabled": not DEBUG,
}
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": f"{os.getenv('CLOUD_NAME')}",
    "API_KEY": f"{os.getenv('API_KEY')}",
    "API_SECRET": f"{os.getenv('API_SECRET')}",
}

EMAIL_BACKEND = f"{os.getenv('EMAIL_BACKEND')}"
EMAIL_HOST = f"{os.getenv('EMAIL_HOST')}"
EMAIL_PORT = f"{os.getenv('EMAIL_PORT')}"
EMAIL_USE_TLS = f"{os.getenv('EMAIL_USE_TLS')}"
EMAIL_HOST_USER = f"{os.getenv('EMAIL_HOST_USER')}"
EMAIL_HOST_PASSWORD = f"{os.getenv('EMAIL_HOST_PASSWORD')}"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

STATICFILES_STORAGE = "cloudinary_storage.storage.StaticHashedCloudinaryStorage"
