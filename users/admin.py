# users/admin.py
"""
Django admin configuration for users app
========================================
Custom admin interface for User, WebsiteQuote, and Newsletter models.

Author: Isaac
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import timedelta
import json

from .models import User, WebsiteQuote, Newsletter
from .tasks import send_quote_email, send_newsletter_email


# ============================================================================
# FILTERS
# ============================================================================

class CreatedDateFilter(SimpleListFilter):
    """Filter by creation date ranges"""
    title = _('Created Date')
    parameter_name = 'created_date'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('week', _('This Week')),
            ('month', _('This Month')),
            ('quarter', _('This Quarter')),
            ('year', _('This Year')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        elif self.value() == 'week':
            start_week = now - timedelta(days=now.weekday())
            return queryset.filter(created_at__gte=start_week)
        elif self.value() == 'month':
            return queryset.filter(
                created_at__year=now.year,
                created_at__month=now.month
            )
        elif self.value() == 'quarter':
            quarter = (now.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            return queryset.filter(
                created_at__year=now.year,
                created_at__month__gte=start_month,
                created_at__month__lt=start_month + 3
            )
        elif self.value() == 'year':
            return queryset.filter(created_at__year=now.year)
        
        return queryset


class BudgetRangeFilter(SimpleListFilter):
    """Filter quotes by budget range"""
    title = _('Budget Range')
    parameter_name = 'budget'

    def lookups(self, request, model_admin):
        return WebsiteQuote.BUDGET_RANGES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(budget_range=self.value())
        return queryset


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class WebsiteQuoteInline(admin.TabularInline):
    """Inline for displaying user's quotes in User admin"""
    model = WebsiteQuote
    fields = ('website_type', 'status', 'budget_range', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# MODEL ADMIN CLASSES
# ============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with custom fields and actions"""
    
    # List display
    list_display = (
        'email', 'get_full_name_display', 'company_name', 
        'is_active', 'is_verified', 'date_joined', 'quotes_count'
    )
    
    list_filter = (
        'is_active', 'is_verified', 'is_staff', 'is_superuser',
        'newsletter_subscription', CreatedDateFilter
    )
    
    search_fields = ('email', 'first_name', 'last_name', 'company_name', 'phone_number')
    ordering = ('-date_joined',)
    
    # Fieldsets for user detail view
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'phone_number', 
                'bio', 'avatar'
            )
        }),
        (_('Business info'), {
            'fields': ('company_name', 'website')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'is_verified', 'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Preferences'), {
            'fields': ('newsletter_subscription',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'last_login_ip'),
            'classes': ('collapse',)
        }),
    )
    
    # Add fieldsets for creating new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2', 'is_staff'
            ),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'last_login_ip')
    
    # Inlines
    inlines = [WebsiteQuoteInline]
    
    # Custom methods for list display
    def get_full_name_display(self, obj):
        """Display full name with email fallback"""
        name = obj.get_full_name()
        if name != obj.email.split('@')[0]:
            return name
        return format_html('<em>{}</em>', obj.email.split('@')[0])
    get_full_name_display.short_description = 'Name'
    get_full_name_display.admin_order_field = 'first_name'
    
    def quotes_count(self, obj):
        """Display number of quotes for this user"""
        count = WebsiteQuote.objects.filter(
            Q(user=obj) | Q(email=obj.email)
        ).count()
        if count > 0:
            url = reverse('admin:users_websitequote_changelist')
            return format_html(
                '<a href="{}?user__id={}">{} quotes</a>',
                url, obj.id, count
            )
        return '0 quotes'
    quotes_count.short_description = 'Quotes'
    
    # Custom actions
    actions = ['verify_users', 'send_newsletter_to_users']
    
    def verify_users(self, request, queryset):
        """Mark selected users as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            f'{updated} users were successfully verified.'
        )
    verify_users.short_description = 'Mark selected users as verified'
    
    def send_newsletter_to_users(self, request, queryset):
        """Send newsletter to selected users"""
        # This would open a form to compose newsletter
        # For now, just show a message
        self.message_user(
            request,
            f'Newsletter functionality would be implemented here for {queryset.count()} users.'
        )
    send_newsletter_to_users.short_description = 'Send newsletter to selected users'


@admin.register(WebsiteQuote)
class WebsiteQuoteAdmin(admin.ModelAdmin):
    """Website Quote admin with enhanced functionality"""
    
    # List display
    list_display = (
        'full_name', 'email', 'website_type', 'status', 
        'budget_range', 'timeline', 'created_at', 'actions_column'
    )
    
    list_filter = (
        'status', 'website_type', BudgetRangeFilter, 
        'timeline', CreatedDateFilter
    )
    
    search_fields = (
        'full_name', 'email', 'company_name', 
        'project_description', 'phone'
    )
    
    ordering = ('-created_at',)
    
    # Fieldsets
    fieldsets = (
        (_('Client Information'), {
            'fields': (
                'full_name', 'email', 'phone', 'company_name', 'user'
            )
        }),
        (_('Project Details'), {
            'fields': (
                'website_type', 'project_description', 
                'budget_range', 'timeline', 'current_website'
            )
        }),
        (_('Features & Requirements'), {
            'fields': ('features_needed_display', 'features_needed_json'),
            'classes': ('collapse',)
        }),
        (_('Admin Section'), {
            'fields': (
                'status', 'estimated_cost', 'admin_notes'
            ),
            'classes': ('wide',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'contacted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'features_needed_display', 'features_needed_json'
    )
    
    # Custom fields for display
    def features_needed_display(self, obj):
        """Display features as readable list"""
        if obj.features_needed:
            features = obj.features_needed
            if isinstance(features, list):
                return format_html('<ul>{}</ul>', 
                    ''.join(f'<li>{feature}</li>' for feature in features)
                )
        return 'No additional features specified'
    features_needed_display.short_description = 'Additional Features'
    
    def features_needed_json(self, obj):
        """Display raw JSON for features"""
        if obj.features_needed:
            return format_html(
                '<pre>{}</pre>', 
                json.dumps(obj.features_needed, indent=2)
            )
        return 'null'
    features_needed_json.short_description = 'Features (JSON)'
    
    def actions_column(self, obj):
        """Action buttons for each quote"""
        buttons = []
        
        if obj.status == 'new':
            buttons.append(
                f'<a href="#" onclick="updateStatus(\'{obj.id}\', \'contacted\')" '
                f'class="button">Mark Contacted</a>'
            )
        
        if obj.status in ['new', 'contacted']:
            buttons.append(
                f'<a href="#" onclick="updateStatus(\'{obj.id}\', \'quoted\')" '
                f'class="button">Send Quote</a>'
            )
        
        return format_html(' '.join(buttons))
    actions_column.short_description = 'Actions'
    actions_column.allow_tags = True
    
    # Custom actions
    actions = ['mark_as_contacted', 'mark_as_quoted', 'resend_confirmation_email']
    
    def mark_as_contacted(self, request, queryset):
        """Mark quotes as contacted"""
        updated = queryset.update(
            status='contacted',
            contacted_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} quotes were marked as contacted.'
        )
    mark_as_contacted.short_description = 'Mark selected quotes as contacted'
    
    def mark_as_quoted(self, request, queryset):
        """Mark quotes as quoted"""
        updated = queryset.update(status='quoted')
        self.message_user(
            request,
            f'{updated} quotes were marked as quoted.'
        )
    mark_as_quoted.short_description = 'Mark selected quotes as quoted'
    
    def resend_confirmation_email(self, request, queryset):
        """Resend confirmation emails"""
        for quote in queryset:
            send_quote_email.delay(quote.id)
        
        self.message_user(
            request,
            f'Confirmation emails are being sent for {queryset.count()} quotes.'
        )
    resend_confirmation_email.short_description = 'Resend confirmation emails'
    
    # Custom save method
    def save_model(self, request, obj, form, change):
        """Custom save to handle status changes"""
        if change:
            # Check if status changed to contacted
            if obj.status == 'contacted' and not obj.contacted_at:
                obj.contacted_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Newsletter subscription admin"""
    
    list_display = (
        'email', 'name', 'is_active', 'subscribed_at', 'unsubscribed_at'
    )
    
    list_filter = ('is_active', CreatedDateFilter)
    search_fields = ('email', 'name')
    ordering = ('-subscribed_at',)
    
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    
    # Custom actions
    actions = ['activate_subscriptions', 'deactivate_subscriptions', 'send_test_newsletter']
    
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions"""
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(
            request,
            f'{updated} subscriptions were activated.'
        )
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        """Deactivate selected subscriptions"""
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(
            request,
            f'{updated} subscriptions were deactivated.'
        )
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'
    
    def send_test_newsletter(self, request, queryset):
        """Send test newsletter to selected subscribers"""
        subscriber_ids = list(queryset.values_list('id', flat=True))
        
        # Send a test newsletter
        send_newsletter_email.delay(
            subscriber_ids=subscriber_ids,
            subject='Test Newsletter from Onehux Web Service',
            content_html='<h1>This is a test newsletter</h1><p>Thank you for subscribing!</p>',
            content_text='This is a test newsletter. Thank you for subscribing!'
        )
        
        self.message_user(
            request,
            f'Test newsletter is being sent to {len(subscriber_ids)} subscribers.'
        )
    send_test_newsletter.short_description = 'Send test newsletter to selected'


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================

admin.site.site_header = 'Onehux Web Service Administration'
admin.site.site_title = 'Onehux Admin'
admin.site.index_title = 'Welcome to Onehux Administration'

# Custom admin dashboard stats (if you want to add dashboard widgets)
def admin_dashboard_stats():
    """Generate dashboard statistics"""
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_quotes': WebsiteQuote.objects.count(),
        'pending_quotes': WebsiteQuote.objects.filter(status='new').count(),
        'newsletter_subscribers': Newsletter.objects.filter(is_active=True).count(),
    }
    return stats