#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
Updated for Onehux Web Service with environment detection.
"""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Detect environment and set appropriate settings module
    django_env = os.environ.get('DJANGO_ENV', 'production')  # Default to production for safety
    
    if django_env == 'development':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.dev')
        os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent / 'dev.env'))
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.prod')
        os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent / 'prod.env'))
    
    print(f"🌍 Environment: {django_env}")
    print(f"⚙️  Settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"📁 Env file: {os.environ.get('DJANGO_ENV_FILE')}")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Special handling for common development commands
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Remind about Tailwind CSS for runserver
        if command == 'runserver' and django_env == 'development':
            print("\n💡 Don't forget to run Tailwind CSS in watch mode:")
            print("   npm run watch")
            print("   or")
            print("   npm run dev\n")
        
        # Remind about Celery for certain commands
        if command in ['migrate', 'runserver'] and django_env == 'development':
            print("💡 For full functionality, also run:")
            print("   celery -A website worker --loglevel=info")
            print("   celery -A website beat --loglevel=info\n")
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


    

# #!/usr/bin/env python
# import os
# import sys
# from pathlib import Path

# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.prod')

#     # Set default env variables if not already set
#     os.environ.setdefault('DJANGO_ENV', 'production')
#     os.environ.setdefault('DJANGO_ENV_FILE', str(Path(__file__).resolve().parent / 'website/.env.prod'))

#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Ensure it's installed and "
#             "available on your PYTHONPATH environment variable. Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)

# if __name__ == '__main__':
#     main()