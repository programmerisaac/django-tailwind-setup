# website/settings/base.py
"""
Base Django settings for Onehux Web Service
==========================================
Common settings shared between development and production environments.

Author: Isaac
"""

import environ
import os
import logging
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from pathlib import Path

logger = logging.getLogger(__name__)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Creating an instance of Env class for managing environment variables
env = environ.Env()

# Read the environment file passed via environment variable or default to `dev.env`
ENV_PATH = os.getenv('DJANGO_ENV_FILE', BASE_DIR / 'dev.env')
environ.Env.read_env(env_file=ENV_PATH)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Core Django Configuration
ROOT_URLCONF = 'website.urls'
WSGI_APPLICATION = 'website.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site Configuration
SITE_ID = env.int("SITE_ID", default=1)
BASE_URL = env.str("BASE_URL", default="http://localhost:8000")

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',#Added
    'django.contrib.sites',#Added
]

THIRD_PARTY_APPS = [
    'django_htmx',
    'corsheaders',
]

LOCAL_APPS = [
    'users',
    'pages',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware Configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pages.middleware.MaintenanceMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# Template Configuration
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
                'pages.context_processors.site_context',  # Custom context processor
            ],
        },
    },
]

# Database Configuration (base - will be extended in environment-specific files)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': env('DB_SSL_MODE', default='prefer'),
        },
        'CONN_MAX_AGE': 600,
    }
}

# Admin Login Path
ADMIN_LOGIN_PATH = env.str('ADMIN_LOGIN_PATH', default='/admin/')

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Authentication URLs
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
LOGIN_REDIRECT_URL = 'users:dashboard'  
LOGOUT_REDIRECT_URL = 'pages:home'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('de', 'Deutsch'),
    ('pt', 'Português'),
    ('zh', '中文'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'website/static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Absolute URLs for media and static files
MEDIA_URL_BASE = f"{BASE_URL}/media/"
STATIC_URL_BASE = f"{BASE_URL}/static/"

# Onehux Company Information
ONEHUX_COMPANY_INFO = {
    'NAME': 'Onehux Web Service',
    'SLOGAN': 'Professional Website Development for Your Business',
    'ADDRESS': 'Professional Web Development Services Worldwide',
    'SUPPORT_EMAIL': env('SUPPORT_EMAIL', default='support@onehux.com'),
    'CONTACT_EMAIL': env('CONTACT_EMAIL', default='support@onehux.com'),
    'PHONE_SUPPORT': env('PHONE_SUPPORT', default='+1 (555) 123-4567'),
    'PHONE_ENQUIRY': env('PHONE_ENQUIRY', default='+1 (555) 987-6543'),
    'SOCIAL_MEDIA': {
        'FACEBOOK': 'https://facebook.com/onehuxwebservice',
        'INSTAGRAM': 'https://instagram.com/onehuxwebservice',
        'X': 'https://x.com/onehuxweb',
        'LINKEDIN': 'https://linkedin.com/company/onehuxwebservice',
        'YOUTUBE': 'https://youtube.com/@onehuxwebservice',
    }
}

# Brand Colors
ONEHUX_COLORS = {
    'PRIMARY': '#154bba',  # Blue
    'SECONDARY': '#f9d000',  # Yellow
    'SUCCESS': '#10b981',  # Green
    'ERROR': '#ef4444',  # Red
    'WARNING': '#f59e0b',  # Orange
    'INFO': '#3b82f6',  # Light Blue
}

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================

SITE_NAME = env.str('SITE_NAME', default='onehux_web_service')

CELERY_TASK_DEFAULT_QUEUE = f'{SITE_NAME}_queue'

REDIS_HOST = env.str('REDIS_HOST', default='localhost')
REDIS_PORT = env.int('REDIS_PORT', default=6379)
REDIS_PASSWORD = env.str('REDIS_PASSWORD', default='')
REDIS_BROKER_DB = env.int('REDIS_BROKER_DB', default=0)
REDIS_RESULTS_DB = env.int('REDIS_RESULTS_DB', default=1)
REDIS_CACHE_DB = env.int('REDIS_CACHE_DB', default=2)
REDIS_SESSIONS_DB = env.int('REDIS_SESSIONS_DB', default=3)

def build_redis_url(db_number):
    """Build Redis URL with credentials from environment"""
    if REDIS_PASSWORD:
        return f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{db_number}"
    return f"redis://{REDIS_HOST}:{REDIS_PORT}/{db_number}"

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', default=build_redis_url(REDIS_BROKER_DB))
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default=build_redis_url(REDIS_RESULTS_DB))

# Basic Celery Settings
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ACKS_LATE = True
CELERY_RESULT_EXPIRES = 3600
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_RESULT_PERSISTENT = True
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_DEFAULT_RETRY_DELAY = 60
CELERY_TASK_MAX_RETRIES = 3

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': build_redis_url(REDIS_CACHE_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': f'onehux_web_{BASE_URL.replace(".", "_").replace(":", "_")}',
        'TIMEOUT': 3600,
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': build_redis_url(REDIS_SESSIONS_DB),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': f'session_{BASE_URL.replace(".", "_").replace(":", "_")}',
        'TIMEOUT': 86400,
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True

# Admin and manager configuration
admin_pairs = env.list('ADMINS', default=[])
ADMINS = [tuple(admin.split(':', 1)) for admin in admin_pairs if ':' in admin]
MANAGERS = ADMINS

# Maintenance configuration
MAINTENANCE_MODE = env.bool("MAINTENANCE_MODE", default=False)
ALLOWED_IP_TO_ADMIN_PAGE = env.list("ALLOWED_IP_TO_ADMIN_PAGE", default=[])
ALLOWED_IP_DURING_SITE_MAINTENANCE = env.list("ALLOWED_IP_DURING_SITE_MAINTENANCE", default=[])

# Rate limiting
RATELIMIT_ENABLE = env.bool('RATELIMIT_ENABLE', default=True)
RATELIMIT_USE_CACHE = 'default'

# Base logging configuration
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [{name}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'general.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Email configuration for production
EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='support@onehux.com')
SERVER_EMAIL = env.str('SERVER_EMAIL', default='support@onehux.com')

# ============================================================================
# SEO AND METADATA CONFIGURATION
# ============================================================================
SITE_META = {
    'site_name': 'Onehux Web Service',
    'site_description': 'Professional website development services for businesses, e-commerce, portfolios, and web applications. Get a custom website that grows your business.',
    'site_keywords': 'website development, web design, business websites, e-commerce development, professional web services',
    'site_author': 'Onehux Web Service',
    'og_image': '/static/images/og-image.jpg',
    'twitter_card': 'summary_large_image',
    'twitter_site': '@onehuxweb',
}

# ============================================================================
# SECURITY SETTINGS (Base)
# ============================================================================
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# CORS settings (will be overridden in environment-specific files)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# CSRF settings
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'