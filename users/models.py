# users/models.py
"""
User models for Onehux Web Service
==================================
Custom user model with additional fields for business requirements.

Author: Isaac
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.urls import reverse
import uuid


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Adds business-specific fields and functionality
    """
    
    # Primary key using UUID for better security
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_("Unique identifier for the user")
    )
    
    # Enhanced user information
    email = models.EmailField(
        _('email address'), 
        unique=True,
        help_text=_("User's email address - used for login")
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text=_("Contact phone number")
    )
    
    # Business information
    company_name = models.CharField(
        max_length=255, 
        blank=True,
        help_text=_("Company or organization name")
    )
    
    website = models.URLField(
        blank=True,
        help_text=_("Current website URL if any")
    )
    
    # Profile information
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text=_("Brief description about user or business")
    )
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        help_text=_("Profile picture")
    )
    
    # Account status and preferences
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Whether user has verified their email address")
    )
    
    newsletter_subscription = models.BooleanField(
        default=True,
        help_text=_("Whether user wants to receive newsletters")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Override username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip() or self.email.split('@')[0]
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    def get_initials(self):
        """Return user initials for avatar display"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[0].upper()


class WebsiteQuote(models.Model):
    """
    Model to store website development quote requests
    """
    
    WEBSITE_TYPES = [
        ('business', _('Business Website')),
        ('ecommerce', _('E-commerce Store')),
        ('portfolio', _('Portfolio Website')),
        ('blog', _('Blog/News Website')),
        ('landing', _('Landing Page')),
        ('web_app', _('Web Application')),
        ('custom', _('Custom Solution')),
    ]
    
    BUDGET_RANGES = [
        ('500-1000', _('$500 - $1,000')),
        ('1000-2500', _('$1,000 - $2,500')),
        ('2500-5000', _('$2,500 - $5,000')),
        ('5000-10000', _('$5,000 - $10,000')),
        ('10000+', _('$10,000+')),
        ('not_sure', _('Not Sure')),
    ]
    
    TIMELINE_CHOICES = [
        ('asap', _('ASAP (Rush Job)')),
        ('1_month', _('Within 1 Month')),
        ('2_months', _('Within 2 Months')),
        ('3_months', _('Within 3 Months')),
        ('flexible', _('Flexible Timeline')),
    ]
    
    STATUS_CHOICES = [
        ('new', _('New Request')),
        ('contacted', _('Client Contacted')),
        ('quoted', _('Quote Sent')),
        ('approved', _('Quote Approved')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    # Primary key
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    # Client Information
    full_name = models.CharField(
        max_length=255,
        help_text=_("Client's full name")
    )
    
    email = models.EmailField(
        help_text=_("Client's email address")
    )
    
    phone = models.CharField(
        max_length=20,
        help_text=_("Client's phone number")
    )
    
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Company or organization name")
    )
    
    # Project Details
    website_type = models.CharField(
        max_length=50,
        choices=WEBSITE_TYPES,
        help_text=_("Type of website needed")
    )
    
    project_description = models.TextField(
        help_text=_("Detailed description of the project requirements")
    )
    
    budget_range = models.CharField(
        max_length=20,
        choices=BUDGET_RANGES,
        help_text=_("Expected budget range")
    )
    
    timeline = models.CharField(
        max_length=20,
        choices=TIMELINE_CHOICES,
        help_text=_("Desired project timeline")
    )
    
    # Additional Features
    features_needed = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of specific features needed")
    )
    
    current_website = models.URLField(
        blank=True,
        help_text=_("Current website URL if any")
    )
    
    # Admin fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Estimated project cost")
    )
    
    admin_notes = models.TextField(
        blank=True,
        help_text=_("Internal notes for admin use")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    
    # Relations
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Associated user account if available")
    )
    
    class Meta:
        db_table = 'users_website_quote'
        verbose_name = _('Website Quote Request')
        verbose_name_plural = _('Website Quote Requests')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.get_website_type_display()}"
    
    def get_absolute_url(self):
        return reverse('users:quote_detail', kwargs={'pk': self.pk})
    
    @property
    def is_new(self):
        return self.status == 'new'
    
    @property
    def estimated_cost_display(self):
        if self.estimated_cost:
            return f"${self.estimated_cost:,.2f}"
        return "Not estimated"


class Newsletter(models.Model):
    """
    Model to store newsletter subscriptions
    """
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users_newsletter'
        verbose_name = _('Newsletter Subscription')
        verbose_name_plural = _('Newsletter Subscriptions')
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    



