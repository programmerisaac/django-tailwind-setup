import os

# Detect environment
env = os.getenv('DJANGO_ENV', 'production')#default to production
print("this is the env ===",env)
if env == 'production':
    from .prod import *
else:
    from .dev import *
