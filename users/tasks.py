# users/tasks.py
"""
Celery tasks for user management and email notifications
======================================================
Asynchronous tasks for sending emails, user management, and system maintenance.

Author: Isaac
"""

from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging
import json

from .models import WebsiteQuote, Newsletter

User = get_user_model()
logger = logging.getLogger(__name__)


# ============================================================================
# EMAIL TASKS
# ============================================================================

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id):
    """
    Send welcome email to newly registered user
    """
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to Onehux Web Service!'
        
        # HTML email content
        html_content = render_to_string('emails/welcome_email.html', {
            'user': user,
            'site_name': 'Onehux Web Service',
            'site_url': settings.BASE_URL,
            'login_url': f"{settings.BASE_URL}/login/",
            'dashboard_url': f"{settings.BASE_URL}/dashboard/",
        })
        
        # Plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Welcome email sent successfully to {user.email}")
        return f"Welcome email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return f"User with ID {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send welcome email to user {user_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return f"Failed to send welcome email after {self.max_retries} retries"


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_quote_email(self, quote_id):
    """
    Send quote confirmation emails to both client and admin
    """
    try:
        quote = WebsiteQuote.objects.get(id=quote_id)
        
        # Send confirmation to client
        client_result = send_quote_confirmation_to_client(quote)
        
        # Send notification to admin
        admin_result = send_quote_notification_to_admin(quote)
        
        logger.info(f"Quote emails sent for quote {quote_id}")
        return f"Quote emails sent for {quote.full_name} - Client: {client_result}, Admin: {admin_result}"
        
    except WebsiteQuote.DoesNotExist:
        logger.error(f"Quote with ID {quote_id} not found")
        return f"Quote with ID {quote_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send quote emails for {quote_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return f"Failed to send quote emails after {self.max_retries} retries"


def send_quote_confirmation_to_client(quote):
    """Send quote confirmation email to client"""
    try:
        subject = f'Thank you for your website quote request - Onehux'
        
        # Calculate estimated timeline
        timeline_map = {
            'asap': 'Rush delivery (additional fees apply)',
            '1_month': '2-4 weeks',
            '2_months': '4-8 weeks',
            '3_months': '8-12 weeks',
            'flexible': 'Flexible timeline'
        }
        
        estimated_timeline = timeline_map.get(quote.timeline, 'To be determined')
        
        # HTML email content
        html_content = render_to_string('emails/quote_confirmation.html', {
            'quote': quote,
            'estimated_timeline': estimated_timeline,
            'site_name': 'Onehux Web Service',
            'site_url': settings.BASE_URL,
            'contact_email': settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL'],
            'support_phone': settings.ONEHUX_COMPANY_INFO['PHONE_SUPPORT'],
        })
        
        # Plain text version
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL'],
            to=[quote.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        return "Success"
        
    except Exception as e:
        logger.error(f"Failed to send quote confirmation to client: {e}")
        return f"Failed: {str(e)}"


def send_quote_notification_to_admin(quote):
    """Send quote notification email to admin"""
    try:
        subject = f'New Website Quote Request from {quote.full_name}'
        
        # Estimate project value
        budget_values = {
            '500-1000': '$500 - $1,000',
            '1000-2500': '$1,000 - $2,500',
            '2500-5000': '$2,500 - $5,000',
            '5000-10000': '$5,000 - $10,000',
            '10000+': '$10,000+',
            'not_sure': 'Not specified'
        }
        
        budget_display = budget_values.get(quote.budget_range, 'Unknown')
        
        # HTML email content
        html_content = render_to_string('emails/quote_admin_notification.html', {
            'quote': quote,
            'budget_display': budget_display,
            'site_url': settings.BASE_URL,
            'admin_url': f"{settings.BASE_URL}/admin/users/websitequote/{quote.id}/change/",
            'features_list': ', '.join(quote.features_needed) if quote.features_needed else 'None specified',
        })
        
        # Plain text version
        text_content = strip_tags(html_content)
        
        # Send to admin emails
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if not admin_emails:
            admin_emails = [settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL']]
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        return "Success"
        
    except Exception as e:
        logger.error(f"Failed to send quote notification to admin: {e}")
        return f"Failed: {str(e)}"


@shared_task(bind=True, max_retries=2)
def send_newsletter_email(self, subscriber_ids, subject, content_html, content_text=None):
    """
    Send newsletter email to list of subscribers
    """
    try:
        subscribers = Newsletter.objects.filter(
            id__in=subscriber_ids,
            is_active=True
        )
        
        sent_count = 0
        failed_count = 0
        
        for subscriber in subscribers:
            try:
                # Create personalized email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=content_text or strip_tags(content_html),
                    from_email=settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL'],
                    to=[subscriber.email]
                )
                
                if content_html:
                    email.attach_alternative(content_html, "text/html")
                
                email.send()
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send newsletter to {subscriber.email}: {e}")
                failed_count += 1
        
        result = f"Newsletter sent: {sent_count} successful, {failed_count} failed"
        logger.info(result)
        return result
        
    except Exception as exc:
        logger.error(f"Newsletter task failed: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300)  # 5 minutes
        
        return f"Newsletter task failed after retries: {exc}"


# ============================================================================
# SYSTEM MAINTENANCE TASKS
# ============================================================================

@shared_task
def cleanup_expired_sessions():
    """
    Clean up expired sessions and inactive users
    """
    try:
        from django.contrib.sessions.models import Session
        
        # Clean expired sessions
        Session.objects.filter(expire_date__lt=timezone.now()).delete()
        
        # Clean up unverified users older than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)
        unverified_users = User.objects.filter(
            is_verified=False,
            date_joined__lt=cutoff_date,
            last_login__isnull=True
        )
        
        deleted_count = unverified_users.count()
        unverified_users.delete()
        
        logger.info(f"Cleanup completed: {deleted_count} unverified users removed")
        return f"Cleanup completed: {deleted_count} unverified users removed"
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        return f"Cleanup task failed: {e}"


@shared_task
def analyze_user_activity_patterns():
    """
    Analyze user activity patterns for insights
    """
    try:
        from django.db.models import Count
        
        # Analyze quote patterns
        total_quotes = WebsiteQuote.objects.count()
        
        # Quote status distribution
        status_distribution = WebsiteQuote.objects.values('status').annotate(
            count=Count('status')
        )
        
        # Popular website types
        popular_types = WebsiteQuote.objects.values('website_type').annotate(
            count=Count('website_type')
        ).order_by('-count')[:5]
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_quotes = WebsiteQuote.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        analysis = {
            'total_quotes': total_quotes,
            'recent_quotes_30_days': recent_quotes,
            'status_distribution': list(status_distribution),
            'popular_website_types': list(popular_types),
            'analysis_date': timezone.now().isoformat()
        }
        
        logger.info(f"User activity analysis completed: {json.dumps(analysis, indent=2)}")
        return analysis
        
    except Exception as e:
        logger.error(f"Activity analysis failed: {e}")
        return f"Activity analysis failed: {e}"


@shared_task
def generate_weekly_analytics():
    """
    Generate weekly analytics report
    """
    try:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        # Weekly metrics
        new_users = User.objects.filter(
            date_joined__range=(start_date, end_date)
        ).count()
        
        new_quotes = WebsiteQuote.objects.filter(
            created_at__range=(start_date, end_date)
        ).count()
        
        completed_projects = WebsiteQuote.objects.filter(
            status='completed',
            updated_at__range=(start_date, end_date)
        ).count()
        
        newsletter_signups = Newsletter.objects.filter(
            subscribed_at__range=(start_date, end_date)
        ).count()
        
        analytics = {
            'period': f"{start_date.date()} to {end_date.date()}",
            'new_users': new_users,
            'new_quotes': new_quotes,
            'completed_projects': completed_projects,
            'newsletter_signups': newsletter_signups,
        }
        
        logger.info(f"Weekly analytics: {json.dumps(analytics)}")
        
        # Send analytics email to admins if configured
        if settings.ADMINS:
            send_analytics_email.delay(analytics)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Weekly analytics generation failed: {e}")
        return f"Weekly analytics failed: {e}"


@shared_task
def send_analytics_email(analytics_data):
    """
    Send analytics report via email
    """
    try:
        subject = f"Weekly Analytics Report - {analytics_data['period']}"
        
        html_content = render_to_string('emails/analytics_report.html', {
            'analytics': analytics_data,
            'site_name': 'Onehux Web Service',
        })
        
        text_content = strip_tags(html_content)
        
        admin_emails = [admin[1] for admin in settings.ADMINS]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails
        )
        email.attach_alternative(html_content, "text/html")
        
        email.send()
        
        return "Analytics email sent successfully"
        
    except Exception as e:
        logger.error(f"Failed to send analytics email: {e}")
        return f"Failed to send analytics email: {e}"


@shared_task
def worker_health_check():
    """
    Health check task to ensure workers are functioning
    """
    return {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'worker_id': worker_health_check.request.id
    }


@shared_task
def database_maintenance():
    """
    Perform database maintenance tasks
    """
    try:
        from django.db import connection
        
        # Update quote statistics
        quote_count = WebsiteQuote.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Vacuum analyze (PostgreSQL specific)
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            with connection.cursor() as cursor:
                cursor.execute("VACUUM ANALYZE;")
        
        maintenance_result = {
            'total_quotes': quote_count,
            'active_users': active_users,
            'maintenance_date': timezone.now().isoformat()
        }
        
        logger.info(f"Database maintenance completed: {maintenance_result}")
        return maintenance_result
        
    except Exception as e:
        logger.error(f"Database maintenance failed: {e}")
        return f"Database maintenance failed: {e}"
    
