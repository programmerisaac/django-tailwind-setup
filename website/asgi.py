# website/asgi.py
"""
ASGI config for Onehux Web Service project.
"""

import os
from pathlib import Path
from django.core.asgi import get_asgi_application

# Detect environment and set appropriate settings module
django_env = os.environ.get('DJANGO_ENV', 'production')  # Default to production

if django_env == 'development':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.dev')
    os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent.parent / 'dev.env'))
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.prod')
    os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent.parent / 'prod.env'))

application = get_asgi_application()




# """
# ASGI config for website project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

# application = get_asgi_application()
