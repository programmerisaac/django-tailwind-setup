# users/apps.py
"""
Users app configuration
======================
Django app configuration for the users application.

Author: Isaac
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """Configuration for the users app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Users')
    
    def ready(self):
        """
        Called when the app is ready.
        Import signals and perform any necessary initialization.
        """
        try:
            # Import signals to ensure they are registered
            from . import signals
        except ImportError:
            # Signals module doesn't exist yet
            pass