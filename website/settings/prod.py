# website/settings/prod.py
"""
Production Django settings for Onehux Web Service
===============================================
Production-specific settings that inherit from base.py
Optimized for production deployment with nginx/gunicorn.

Author: Isaac
"""

from .base import *
import environ
import logging
from celery.schedules import crontab
from datetime import timedelta

# Override environment file for production
env = environ.Env()
environ.Env.read_env(BASE_DIR / 'prod.env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

# Production allowed hosts (strict)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    'onehuxwebservice.com',
    'www.onehuxwebservice.com',
    '*.onehuxwebservice.com',
])

# ============================================================================
# PRODUCTION DATABASE CONFIGURATION (OPTIMIZED)
# ============================================================================
DATABASES['default'].update({
    'OPTIONS': {
        'sslmode': env('DB_SSL_MODE', default='require'),
        'connect_timeout': 10,
        'keepalives_idle': 600,
        'keepalives_interval': 30,
        'keepalives_count': 3,
    },
    'CONN_MAX_AGE': 600,
    'MAX_CONNS': 20,
})

# ============================================================================
# PRODUCTION SECURITY SETTINGS (MAXIMUM SECURITY)
# ============================================================================

USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Cookie Security (strict for production)
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# ============================================================================
# CORS SETTINGS (PRODUCTION - STRICT)
# ============================================================================
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    "https://onehuxwebservice.com",
    "https://www.onehuxwebservice.com",
])

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

CSRF_TRUSTED_ORIGINS = [
    'https://onehuxwebservice.com',
    'https://www.onehuxwebservice.com',
]

# ============================================================================
# PRODUCTION CELERY CONFIGURATION
# ============================================================================
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_TASK_STORE_EAGER_RESULT = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes hard limit

# Production Celery Beat Configuration
CELERY_BEAT_ENABLED = env.bool('CELERY_BEAT_ENABLED', default=True)

if CELERY_BEAT_ENABLED:
    CELERY_BEAT_SCHEDULE = {
        # Session cleanup - Daily at 2 AM
        f'{SITE_NAME}_cleanup_expired_sessions': {
            'task': 'users.tasks.cleanup_expired_sessions',
            'schedule': crontab(hour=2, minute=0),
        },
        # Weekly analytics report - Mondays at 1 AM
        f'{SITE_NAME}_generate_weekly_reports': {
            'task': 'users.tasks.generate_weekly_analytics',
            'schedule': crontab(hour=1, minute=0, day_of_week=1),
        },
        # User activity analysis - Every 6 hours
        f'{SITE_NAME}_analyze_user_activity': {
            'task': 'users.tasks.analyze_user_activity_patterns',
            'schedule': crontab(minute=0, hour='*/6'),
        },
        # Daily health check - Every morning at 6 AM
        f'{SITE_NAME}_daily_health_check': {
            'task': 'users.tasks.worker_health_check',
            'schedule': crontab(hour=6, minute=0),
        },
        # Database maintenance - Every Sunday at 3 AM
        f'{SITE_NAME}_database_maintenance': {
            'task': 'users.tasks.database_maintenance',
            'schedule': crontab(hour=3, minute=0, day_of_week=0),
        },
    }
else:
    CELERY_BEAT_SCHEDULE = {}

# ============================================================================
# PRODUCTION LOGGING CONFIGURATION
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
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s %(pathname)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'production.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
        'file_celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'celery_production.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 10,
            'formatter': 'celery',
        },
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'security.log'),
            'maxBytes': 1024 * 1024 * 20,  # 20MB
            'backupCount': 15,
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'errors.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general', 'file_error', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file_celery'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery.task': {
            'handlers': ['file_celery'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['file_general', 'file_error', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'users.tasks': {
            'handlers': ['file_celery'],
            'level': 'INFO',
            'propagate': False,
        },
        'pages': {
            'handlers': ['file_general', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file_general', 'file_error'],
            'level': 'INFO',
            'propagate': True,
        },
    },
})

# ============================================================================
# PRODUCTION CACHE CONFIGURATION (OPTIMIZED)
# ============================================================================
CACHES['default'].update({
    'TIMEOUT': 3600,  # 1 hour
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        'CONNECTION_POOL_KWARGS': {
            'max_connections': 100,
            'retry_on_timeout': True,
            'socket_keepalive': True,
            'socket_keepalive_options': {},
        },
        'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        'IGNORE_EXCEPTIONS': True,
    },
})

CACHES['sessions'].update({
    'TIMEOUT': 86400,  # 24 hours
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        'CONNECTION_POOL_KWARGS': {
            'max_connections': 50,
            'retry_on_timeout': True,
            'socket_keepalive': True,
        },
        'IGNORE_EXCEPTIONS': True,
    },
})

# ============================================================================
# STATIC FILES CONFIGURATION (FOR NGINX)
# ============================================================================
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise configuration
WHITENOISE_USE_FINDERS = False
WHITENOISE_AUTOREFRESH = False
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# ============================================================================
# EMAIL CONFIGURATION (PRODUCTION)
# ============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# ============================================================================
# ENVIRONMENT INDICATOR
# ============================================================================
ENVIRONMENT = 'production'

# Production warning check
if DEBUG:
    import warnings
    warnings.warn("DEBUG=True in production settings! This should be False in production.")

print(f"""
🚀 PRODUCTION CONFIGURATION LOADED
===================================
Debug Mode: {DEBUG}
Environment: {ENVIRONMENT}
Database: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}
Redis: {CELERY_BROKER_URL.split('@')[-1] if '@' in CELERY_BROKER_URL else CELERY_BROKER_URL}
SSL Redirect: {SECURE_SSL_REDIRECT}
Celery Beat: {CELERY_BEAT_ENABLED}
Static Storage: {STATICFILES_STORAGE}
===================================
""")