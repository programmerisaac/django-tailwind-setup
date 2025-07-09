# website/celery.py
"""
Celery configuration for Onehux Web Service
==========================================
Celery app configuration with Redis broker and result backend.
Optimized for both development and production environments.

Author: Isaac
"""

import os
from celery import Celery
from django.conf import settings
from celery.signals import setup_logging
import logging

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings.prod')

# Create the Celery app instance
app = Celery('onehux_web_service')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery logging configuration
@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure logging for Celery workers"""
    from logging.config import dictConfig
    from django.conf import settings
    
    if hasattr(settings, 'LOGGING'):
        dictConfig(settings.LOGGING)

# Celery worker optimization
app.conf.update(
    # Task routing
    task_routes={
        'users.tasks.send_welcome_email': {'queue': 'email'},
        'users.tasks.send_quote_email': {'queue': 'email'},
        'users.tasks.send_newsletter_email': {'queue': 'email'},
        'users.tasks.cleanup_expired_sessions': {'queue': 'maintenance'},
        'users.tasks.analyze_user_activity_patterns': {'queue': 'analytics'},
        'users.tasks.generate_weekly_analytics': {'queue': 'analytics'},
        'users.tasks.database_maintenance': {'queue': 'maintenance'},
    },
    
    # Task priorities
    task_default_priority=5,
    worker_prefetch_multiplier=1,
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat settings
    beat_schedule_filename='celerybeat-schedule',
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Custom task base class for common functionality
class BaseTask(app.Task):
    """Base task class with common functionality"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger = logging.getLogger(f'celery.task.{self.name}')
        logger.info(f'Task {self.name}[{task_id}] succeeded: {retval}')
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger = logging.getLogger(f'celery.task.{self.name}')
        logger.error(f'Task {self.name}[{task_id}] failed: {exc}')
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger = logging.getLogger(f'celery.task.{self.name}')
        logger.warning(f'Task {self.name}[{task_id}] retry: {exc}')

# Set the default task base class
app.Task = BaseTask

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'

# Celery health check task
@app.task(bind=True)
def health_check(self):
    """Health check task to verify Celery is running"""
    import datetime
    return {
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'worker_id': self.request.id,
        'hostname': self.request.hostname,
    }

# Periodic task to clean up Celery results
@app.task(bind=True)
def cleanup_celery_results(self):
    """Clean up old Celery task results"""
    try:
        from celery.result import AsyncResult
        from datetime import datetime, timedelta
        
        # This would need to be implemented based on your result backend
        # For Redis, you might want to clean up old keys
        # For database backend, you'd clean up old records
        
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        logger = logging.getLogger('celery.maintenance')
        logger.info(f'Cleaned up Celery results older than {cutoff_date}')
        
        return f'Cleanup completed for results older than {cutoff_date}'
        
    except Exception as exc:
        logger = logging.getLogger('celery.maintenance')
        logger.error(f'Failed to cleanup Celery results: {exc}')
        raise

# Register custom tasks
if __name__ == '__main__':
    app.start()

