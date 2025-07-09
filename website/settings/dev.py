# website/settings/dev.py
"""
Development Django settings for Onehux Web Service
================================================
Development-specific settings that inherit from base.py

Author: Isaac
"""

from .base import *
import environ
from datetime import timedelta

# Override environment file for development
env = environ.Env()
environ.Env.read_env(BASE_DIR / 'dev.env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

# Allowed hosts for development
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    'localhost', 
    '127.0.0.1', 
    'dev.onehuxwebservice.com',
    '*'  # Allow all hosts in development
])

# ============================================================================
# DEVELOPMENT DATABASE CONFIGURATION
# ============================================================================
DATABASES['default'].update({
    'OPTIONS': {
        'sslmode': env('DB_SSL_MODE', default='prefer'),
    },
    'CONN_MAX_AGE': 0,  # Don't reuse connections for easier debugging
})

# ============================================================================
# DEVELOPMENT SECURITY SETTINGS (RELAXED)
# ============================================================================
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'

# ============================================================================
# CORS SETTINGS (DEVELOPMENT - RELAXED)
# ============================================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://dev.onehuxwebservice.com',
]

# ============================================================================
# CELERY CONFIGURATION (DEVELOPMENT)
# ============================================================================
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=True)  # Run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_STORE_EAGER_RESULT = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_TASK_TIME_LIMIT = 120

# Celery Beat (disabled by default in development)
CELERY_BEAT_ENABLED = env.bool('CELERY_BEAT_ENABLED', default=False)
CELERY_BEAT_SCHEDULE = {}

if CELERY_BEAT_ENABLED:
    CELERY_BEAT_SCHEDULE = {
        f'{SITE_NAME}_dev_health_check': {
            'task': 'users.tasks.worker_health_check',
            'schedule': timedelta(minutes=5),
        },
        f'{SITE_NAME}_cleanup_expired_sessions': {
            'task': 'users.tasks.cleanup_expired_sessions',
            'schedule': timedelta(minutes=30),
        },
    }

# ============================================================================
# DEVELOPMENT CACHE CONFIGURATION
# ============================================================================
CACHES['default']['TIMEOUT'] = 300  # 5 minutes
CACHES['sessions']['TIMEOUT'] = 1800  # 30 minutes

# ============================================================================
# DEVELOPMENT LOGGING CONFIGURATION
# ============================================================================
LOGGING.update({
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [{name}:{lineno}] {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
        'celery': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'development.log'),
            'formatter': 'verbose',
        },
        'file_celery': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'celery_dev.log'),
            'formatter': 'celery',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file_celery'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['file_celery'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file_general'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users.tasks': {
            'handlers': ['console', 'file_celery'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'pages': {
            'handlers': ['console', 'file_general'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file_general'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
})

# ============================================================================
# RATE LIMITING (DISABLED FOR DEVELOPMENT)
# ============================================================================
RATELIMIT_ENABLE = False

# ============================================================================
# TAILWIND CONFIGURATION
# ============================================================================
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# ============================================================================
# DEVELOPMENT TOOLS
# ============================================================================
DEV_APPS = []

# Django Debug Toolbar
if env.bool('ENABLE_DEBUG_TOOLBAR', default=True):
    DEV_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
    def show_toolbar(request):
        return DEBUG and request.META.get('REMOTE_ADDR') in INTERNAL_IPS
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    }

# Django Extensions
if env.bool('ENABLE_DJANGO_EXTENSIONS', default=False):
    DEV_APPS.append('django_extensions')
    SHELL_PLUS_PRINT_SQL = True
    SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000

# Add development apps
INSTALLED_APPS += DEV_APPS

# ============================================================================
# DEVELOPMENT ENVIRONMENT SETTINGS
# ============================================================================
ENVIRONMENT = 'development'

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Print development configuration summary
if DEBUG:
    print(f"""
🔧 DEVELOPMENT CONFIGURATION LOADED
====================================
Debug Mode: {DEBUG}
Database: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}
Redis: {CELERY_BROKER_URL}
Celery Eager: {CELERY_TASK_ALWAYS_EAGER}
Beat Enabled: {CELERY_BEAT_ENABLED}
CORS Allow All: {CORS_ALLOW_ALL_ORIGINS}
Rate Limiting: {RATELIMIT_ENABLE}
Environment: {ENVIRONMENT}
Email Backend: {EMAIL_BACKEND}
====================================
""")

# Static files configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files served by Django in development
MEDIA_URL = '/media/'