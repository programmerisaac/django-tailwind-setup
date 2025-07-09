# users/signals.py
"""
Django signals for users app
===========================
Handles automatic tasks triggered by model events.

Author: Isaac
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
import logging

from .models import WebsiteQuote, Newsletter
from .tasks import send_quote_email, send_welcome_email

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================================================================
# USER SIGNALS
# ============================================================================

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Handle post-save actions for User model
    """
    if created:
        # Send welcome email for new users
        try:
            send_welcome_email.delay(instance.id)
            logger.info(f"Welcome email queued for user {instance.email}")
        except Exception as e:
            logger.error(f"Failed to queue welcome email for {instance.email}: {e}")
        
        # Clear user-related cache
        cache.delete_many([
            'user_count',
            'recent_users',
            'user_stats'
        ])
        
        logger.info(f"New user created: {instance.email}")
    
    else:
        # Handle user updates
        logger.debug(f"User updated: {instance.email}")


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Handle user login events
    """
    # Update last login IP
    if hasattr(request, 'META'):
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save(update_fields=['last_login_ip'])
    
    logger.info(f"User logged in: {user.email} from {request.META.get('REMOTE_ADDR', 'unknown')}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    Handle user logout events
    """
    if user:
        logger.info(f"User logged out: {user.email}")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    Handle failed login attempts
    """
    username = credentials.get('username', 'unknown')
    ip_address = request.META.get('REMOTE_ADDR', 'unknown') if request else 'unknown'
    
    logger.warning(f"Failed login attempt for {username} from {ip_address}")


# ============================================================================
# QUOTE SIGNALS
# ============================================================================

@receiver(post_save, sender=WebsiteQuote)
def quote_post_save(sender, instance, created, **kwargs):
    """
    Handle post-save actions for WebsiteQuote model
    """
    if created:
        # Send quote emails for new quotes
        try:
            send_quote_email.delay(instance.id)
            logger.info(f"Quote emails queued for quote {instance.id}")
        except Exception as e:
            logger.error(f"Failed to queue quote emails for {instance.id}: {e}")
        
        # Clear quote-related cache
        cache.delete_many([
            'quote_count',
            'recent_quotes',
            'quote_stats',
            'popular_website_types'
        ])
        
        logger.info(f"New quote created: {instance.id} from {instance.email}")
    
    else:
        # Handle quote updates
        logger.debug(f"Quote updated: {instance.id} - Status: {instance.status}")
        
        # Clear cache when quote status changes
        cache.delete_many([
            'quote_stats',
            'recent_quotes'
        ])


@receiver(pre_save, sender=WebsiteQuote)
def quote_pre_save(sender, instance, **kwargs):
    """
    Handle pre-save actions for WebsiteQuote model
    """
    if instance.pk:  # Existing quote
        try:
            old_instance = WebsiteQuote.objects.get(pk=instance.pk)
            
            # Log status changes
            if old_instance.status != instance.status:
                logger.info(f"Quote {instance.id} status changed: {old_instance.status} -> {instance.status}")
                
                # Set contacted_at when status changes to contacted
                if instance.status == 'contacted' and not instance.contacted_at:
                    instance.contacted_at = timezone.now()
        
        except WebsiteQuote.DoesNotExist:
            pass


@receiver(post_delete, sender=WebsiteQuote)
def quote_post_delete(sender, instance, **kwargs):
    """
    Handle post-delete actions for WebsiteQuote model
    """
    logger.info(f"Quote deleted: {instance.id} from {instance.email}")
    
    # Clear quote-related cache
    cache.delete_many([
        'quote_count',
        'recent_quotes',
        'quote_stats',
        'popular_website_types'
    ])


# ============================================================================
# NEWSLETTER SIGNALS
# ============================================================================

@receiver(post_save, sender=Newsletter)
def newsletter_post_save(sender, instance, created, **kwargs):
    """
    Handle post-save actions for Newsletter model
    """
    if created:
        logger.info(f"New newsletter subscription: {instance.email}")
        
        # Clear newsletter cache
        cache.delete('newsletter_count')
        cache.delete('newsletter_stats')
    
    else:
        # Handle newsletter updates
        logger.debug(f"Newsletter subscription updated: {instance.email} - Active: {instance.is_active}")


@receiver(post_delete, sender=Newsletter)
def newsletter_post_delete(sender, instance, **kwargs):
    """
    Handle post-delete actions for Newsletter model
    """
    logger.info(f"Newsletter subscription deleted: {instance.email}")
    
    # Clear newsletter cache
    cache.delete('newsletter_count')
    cache.delete('newsletter_stats')


# ============================================================================
# CACHE INVALIDATION HELPERS
# ============================================================================

def clear_user_cache():
    """Clear all user-related cache"""
    cache.delete_many([
        'user_count',
        'recent_users',
        'user_stats',
        'active_users'
    ])


def clear_quote_cache():
    """Clear all quote-related cache"""
    cache.delete_many([
        'quote_count',
        'recent_quotes',
        'quote_stats',
        'popular_website_types',
        'pending_quotes'
    ])


def clear_all_stats_cache():
    """Clear all statistics cache"""
    cache.delete_many([
        'user_count',
        'quote_count',
        'newsletter_count',
        'user_stats',
        'quote_stats',
        'newsletter_stats',
        'dashboard_stats',
        'homepage_stats'
    ])


# ============================================================================
# PERIODIC CACHE WARMING (Optional)
# ============================================================================

def warm_cache():
    """
    Warm up frequently accessed cache entries
    This can be called by a periodic task
    """
    try:
        # Warm up user stats
        User.objects.filter(is_active=True).count()
        
        # Warm up quote stats
        WebsiteQuote.objects.filter(status='new').count()
        
        # Warm up newsletter stats
        Newsletter.objects.filter(is_active=True).count()
        
        logger.info("Cache warmed successfully")
        
    except Exception as e:
        logger.error(f"Failed to warm cache: {e}")


# ============================================================================
# ERROR HANDLING SIGNALS
# ============================================================================

@receiver(post_save, sender=User)
def handle_user_creation_errors(sender, instance, created, **kwargs):
    """
    Handle any errors that might occur during user creation
    """
    if created:
        try:
            # Validate user data
            if not instance.email:
                logger.warning(f"User {instance.id} created without email")
            
            if not instance.first_name and not instance.last_name:
                logger.warning(f"User {instance.id} created without name")
                
        except Exception as e:
            logger.error(f"Error in user creation handler: {e}")


# ============================================================================
# ANALYTICS SIGNALS
# ============================================================================

@receiver(post_save, sender=WebsiteQuote)
def track_quote_analytics(sender, instance, created, **kwargs):
    """
    Track analytics for quote requests
    """
    if created:
        try:
            # Track quote by type
            cache_key = f"quote_type_count_{instance.website_type}"
            current_count = cache.get(cache_key, 0)
            cache.set(cache_key, current_count + 1, 86400)  # 24 hours
            
            # Track quote by budget range
            cache_key = f"quote_budget_count_{instance.budget_range}"
            current_count = cache.get(cache_key, 0)
            cache.set(cache_key, current_count + 1, 86400)  # 24 hours
            
            # Track daily quote count
            today = timezone.now().date()
            cache_key = f"daily_quotes_{today}"
            current_count = cache.get(cache_key, 0)
            cache.set(cache_key, current_count + 1, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Failed to track quote analytics: {e}")


@receiver(user_logged_in)
def track_login_analytics(sender, request, user, **kwargs):
    """
    Track login analytics
    """
    try:
        # Track daily logins
        today = timezone.now().date()
        cache_key = f"daily_logins_{today}"
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 86400)  # 24 hours
        
        # Track unique daily users
        cache_key = f"daily_unique_users_{today}"
        user_set = cache.get(cache_key, set())
        user_set.add(user.id)
        cache.set(cache_key, user_set, 86400)  # 24 hours
        
    except Exception as e:
        logger.error(f"Failed to track login analytics: {e}")

