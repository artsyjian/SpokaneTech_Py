"""
Django settings for spokanetech project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

import environ
import dj_database_url
import sentry_sdk


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from an env file
ENV_PATH = os.environ.get("ENV_PATH", f"{BASE_DIR.parent}/envs/.env")
env = environ.Env()
if os.path.exists(ENV_PATH):
  print(f"Loading ENV vars from {ENV_PATH}")
  environ.Env.read_env(ENV_PATH)
else:
  print("NO ENV_PATH found!")

ADMINS = [
    ("Organizers", "organizers@spokanetech.org"),
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

IS_DEVELOPMENT = env.bool("SPOKANE_TECH_DEV", default=False)

if IS_DEVELOPMENT:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = "django-insecure-t9*!4^fdn*=pmz4%8u_we!88e!8@_!drx0)u_@6$@!nx$4svjp"  # nosec: Development-only key.

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = []

    INTERNAL_IPS = [
        "localhost",
        "127.0.0.1",
    ]
else:
    try:
        SECRET_KEY = env.str("DJANGO_SECRET_KEY")
    except KeyError as e:
        raise KeyError(f"{e}: If running in development, set 'SPOKANE_TECH_DEV' to any value.") from e

    DEBUG = False
    ALLOWED_HOSTS = env.str(
      "ALLOWED_HOSTS",
      default="spokanetech.org,spokanetech-py.fly.dev"
    ).split(",")
    CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

    # SSL Options
    # TODO: These will have to change depending on how infra-platform handles SSL termination
    # https://docs.djangoproject.com/en/5.0/ref/settings/#secure-hsts-preload
    SECURE_HSTS_SECONDS = 0
    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    if sentry_dsn := env.str("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=0.1,
        )


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "django_celery_results",
    "django_celery_beat",
    "django_filters",
    "crispy_forms",
    "crispy_bootstrap5",
    "markdownify.apps.MarkdownifyConfig",
    "handyhelpers",
    "web",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "web.middleware.TimezoneMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "spokanetech.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "spokanetech.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        conn_health_checks=True,
    ),
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Storages
USE_AZURE = env.bool("USE_AZURE") if env("USE_AZURE") != "" else not DEBUG
if USE_AZURE:
    DEFAULT_FILE_STORAGE = "spokanetech.backend.AzureMediaStorage"
    STATICFILES_STORAGE = "spokanetech.backend.AzureStaticStorage"

    STATIC_LOCATION = "static"
    MEDIA_LOCATION = "media"

    AZURE_URL_EXPIRATION_SECS = None
    AZURE_ACCOUNT_NAME = env.str("AZURE_ACCOUNT_NAME")
    AZURE_ACCOUNT_KEY = env.str("AZURE_ACCOUNT_KEY")
    AZURE_CUSTOM_DOMAIN = env.str(
        "AZURE_CDN_DOMAIN",
        default=f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net",
    )
    STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
    MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"
    MEDIA_UPLOAD_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}"
else:
    STATIC_ROOT = BASE_DIR / "staticfiles"

    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


PROJECT_NAME = "Spokane Tech"
PROJECT_DESCRIPTION = """Community resource for all things tech in the Spokane and CDA area"""
PROJECT_VERSION = "0.0.1"


# Celery
try:
    CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
    CELERY_ENABLED = True
except KeyError:
    if IS_DEVELOPMENT:
        CELERY_ENABLED = False
    else:
        raise

CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default="django-db")
CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# Discord
DISCORD_WEBHOOK_URL = env.str("DISCORD_WEBHOOK_URL")


# Eventbrite
EVENTBRITE_API_TOKEN = env.str("EVENTBRITE_API_TOKEN")


# Markdownify
MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "code",
            "em",
            "i",
            "li",
            "ol",
            "p",
            "strong",
            "ul",
        ]
    },
}


# Django Debug Toolbar
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": {
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
    }
}


# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"


# Email
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="DoNotReply@spokanetech.org")
SERVER_EMAIL = env.str("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

if USE_AZURE:
    EMAIL_BACKEND = "django_azure_communication_email.EmailBackend"
    AZURE_COMMUNICATION_CONNECTION_STRING = env.str("AZURE_COMMUNICATION_CONNECTION_STRING")
