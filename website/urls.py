# website/urls.py
"""
URL configuration for Onehux Web Service project
===============================================
Main URL routing for the website including all app URLs.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Author: Isaac
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import HttpResponse
import os

# Import sitemaps
from pages.sitemaps import StaticViewSitemap, PagesSitemap

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'pages': PagesSitemap,
}

urlpatterns = [
    # ========================================================================
    # ADMIN URLS
    # ========================================================================
    path(settings.ADMIN_LOGIN_PATH.strip('/') + '/', admin.site.urls),
    
    # ========================================================================
    # APP URLS
    # ========================================================================
    
    # Users app (authentication, dashboard, quotes)
    path('', include('users.urls', namespace='users')),
    
    # Pages app (home, about, contact, etc.)
    path('', include('pages.urls', namespace='pages')),
    
    # ========================================================================
    # SEO AND UTILITY URLS
    # ========================================================================
    
    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    
    # Robots.txt (handled by users.views.robots_txt)
    path('robots.txt', include('users.urls')),
    
    # Favicon
    path('favicon.ico', 
         TemplateView.as_view(template_name='favicon.ico', content_type='image/x-icon')),
    
    # Service Worker for PWA
    path('sw.js', include('users.urls')),
    
    # ========================================================================
    # HEALTH CHECK AND MONITORING
    # ========================================================================
    
    # Basic health check endpoint
    path('health/', 
         lambda request: HttpResponse('OK', content_type='text/plain'),
         name='health_check'),
    
    # Status endpoint for monitoring
    path('status/', 
         lambda request: HttpResponse('{"status": "healthy", "service": "onehux-web-service"}', 
                                    content_type='application/json'),
         name='status_check'),
    
    # ========================================================================
    # SECURITY AND VALIDATION URLS
    # ========================================================================
    
    # Security.txt for security researchers
    path('.well-known/security.txt', 
         lambda request: HttpResponse(
             'Contact: mailto:security@onehuxwebservice.com\n'
             'Expires: 2025-12-31T23:59:59.000Z\n'
             'Preferred-Languages: en\n'
             'Canonical: https://onehuxwebservice.com/.well-known/security.txt',
             content_type='text/plain'
         ),
         name='security_txt'),
    
    # Humans.txt for fun
    path('humans.txt', 
         lambda request: HttpResponse(
             '/* TEAM */\n'
             'Developer: Onehux Web Service Team\n'
             'Contact: hello@onehuxwebservice.com\n'
             'From: Professional Web Development Services\n\n'
             '/* THANKS */\n'
             'Django, PostgreSQL, Redis, Celery, Tailwind CSS\n\n'
             '/* SITE */\n'
             'Last update: 2025\n'
             'Language: English\n'
             'Standards: HTML5, CSS3, ES6+\n'
             'Components: Django, Alpine.js, Tailwind CSS\n'
             'Software: VS Code, Git, Linux\n',
             content_type='text/plain'
         ),
         name='humans_txt'),
]

# ============================================================================
# DEVELOPMENT URLS
# ============================================================================
if settings.DEBUG:
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar URLs
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    
    # Development test URLs for email templates and other testing
    urlpatterns += [
        # Test pages (only available in development)
        path('dev/test/email/', 
             TemplateView.as_view(template_name='dev/email_test.html'),
             name='dev_email_test'),
        
        path('dev/test/colors/', 
             TemplateView.as_view(template_name='dev/color_test.html'),
             name='dev_color_test'),
        
        # 500 error page test
        path('dev/test/500/', 
             lambda request: exec('raise Exception("Test 500 error")')),
        
        # 404 error page test  
        path('dev/test/404/', 
             lambda request: HttpResponse(status=404)),
    ]

# ============================================================================
# ERROR HANDLERS
# ============================================================================

# Custom error handlers
handler400 = 'pages.views.bad_request'
handler403 = 'pages.views.permission_denied'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

# ============================================================================
# PRODUCTION-SPECIFIC URLS
# ============================================================================
if not settings.DEBUG:
    # In production, you might want to add additional security measures
    # or monitoring endpoints that are not available in development
    pass

# ============================================================================
# CUSTOM ADMIN CONFIGURATION
# ============================================================================

# Customize admin site headers and titles
admin.site.site_header = 'Onehux Web Service Administration'
admin.site.site_title = 'Onehux Admin Portal'
admin.site.index_title = 'Welcome to Onehux Web Service Administration'

# Customize admin login page
admin.site.login_template = 'admin/custom_login.html'
admin.site.login_form = None  # Use default login form
admin.site.index_template = 'admin/custom_index.html'

# Add custom admin views if needed
# urlpatterns += [
#     path(f'{settings.ADMIN_LOGIN_PATH.strip("/")}/reports/', 
#          admin_views.AdminReportsView.as_view(), 
#          name='admin_reports'),
# ]