#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.prod')

    # Set default env variables if not already set
    os.environ.setdefault('DJANGO_ENV', 'production')
    os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent / 'website/.env.prod'))

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Ensure it's installed and "
            "available on your PYTHONPATH environment variable. Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()