# website/wsgi.py
"""
WSGI config for Onehux Web Service project.
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Detect environment and set appropriate settings module
django_env = os.environ.get('DJANGO_ENV', 'production')  # Default to production

if django_env == 'development':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.dev')
    os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent.parent / 'dev.env'))
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.prod')
    os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent.parent / 'prod.env'))

application = get_wsgi_application()



# """
# WSGI config for website project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

# application = get_wsgi_application()
