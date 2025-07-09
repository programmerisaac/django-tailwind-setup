# users/urls.py
"""
URL configuration for users app
==============================
Defines all URL patterns for user authentication, dashboard, and quote system.

Author: Isaac
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # ========================================================================
    # AUTHENTICATION URLS
    # ========================================================================
    
    # Registration and Login
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='emails/password_reset_email.html',
             subject_template_name='emails/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Password Change URLs (for logged-in users)
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change.html',
             success_url='/password-change/done/'
         ),
         name='password_change'),
    
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'
         ),
         name='password_change_done'),
    
    # ========================================================================
    # USER DASHBOARD & PROFILE URLS
    # ========================================================================
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile Management
    path('profile/', views.profile, name='profile'),
    path('profile/<uuid:pk>/', views.profile, name='profile_detail'),
    
    # ========================================================================
    # WEBSITE QUOTE SYSTEM URLS
    # ========================================================================
    
    # Quote Request
    path('quote/', views.quote_request, name='quote_request'),
    path('quote/success/', views.quote_success, name='quote_success'),
    
    # User's Quotes
    path('my-quotes/', views.my_quotes, name='my_quotes'),
    path('quote/<uuid:pk>/', views.quote_detail, name='quote_detail'),
    
    # ========================================================================
    # AJAX & API ENDPOINTS
    # ========================================================================
    
    # Newsletter Subscription
    path('api/newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Cost Estimation
    path('api/estimate-cost/', views.estimate_cost, name='estimate_cost'),
    
    # ========================================================================
    # UTILITY URLS
    # ========================================================================
    
    # Service Worker for PWA
    path('sw.js', views.service_worker, name='service_worker'),
    
    # SEO Files
    path('robots.txt', views.robots_txt, name='robots_txt'),
]

# Additional URL patterns for development/testing
if __debug__:
    # These URLs are only available in development mode
    test_patterns = [
        # Test email templates
        path('test/email/welcome/', 
             lambda request: views.render(request, 'emails/welcome_email.html', {
                 'user': request.user if request.user.is_authenticated else None,
                 'site_name': 'Onehux Web Service',
                 'site_url': 'http://localhost:8000',
             }), 
             name='test_welcome_email'),
        
        path('test/email/quote-confirmation/', 
             lambda request: views.render(request, 'emails/quote_confirmation.html', {
                 'quote': {
                     'full_name': 'John Doe',
                     'email': 'john@example.com',
                     'website_type': 'business',
                     'project_description': 'A professional business website',
                 },
                 'estimated_timeline': '2-4 weeks',
                 'site_name': 'Onehux Web Service',
             }), 
             name='test_quote_email'),
    ]
    
    urlpatterns += test_patterns




