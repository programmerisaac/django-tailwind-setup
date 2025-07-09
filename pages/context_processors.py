# pages/context_processors.py
"""
Context processors for pages app
===============================
Provides global context variables available in all templates.

Author: Isaac
"""

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.sites.models import Site
import json


def site_context(request):
    """
    Add site-wide context variables to all templates
    """
    context = {
        # Company information
        'company': settings.ONEHUX_COMPANY_INFO,
        
        # Brand colors for easy access in templates
        'colors': settings.ONEHUX_COLORS,
        
        # Site metadata
        'site_meta': getattr(settings, 'SITE_META', {}),
        
        # Current year for copyright
        'current_year': timezone.now().year,
        
        # Environment information
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
        'debug': settings.DEBUG,
        
        # Base URL for absolute URLs
        'base_url': settings.BASE_URL,
        
        # Navigation items
        'main_nav': [
            {
                'name': 'Home',
                'url': reverse('pages:home'),
                'active_patterns': ['pages:home']
            },
            {
                'name': 'About',
                'url': reverse('pages:about'),
                'active_patterns': ['pages:about']
            },
            {
                'name': 'Services',
                'url': reverse('pages:services'),
                'active_patterns': ['pages:services']
            },
            {
                'name': 'Portfolio',
                'url': '#portfolio',  # Will be implemented later
                'active_patterns': []
            },
            {
                'name': 'Contact',
                'url': reverse('pages:contact'),
                'active_patterns': ['pages:contact']
            },
        ],
        
        # Footer navigation
        'footer_nav': {
            'company': [
                {'name': 'About Us', 'url': reverse('pages:about')},
                {'name': 'Our Services', 'url': reverse('pages:services')},
                {'name': 'Contact Us', 'url': reverse('pages:contact')},
                {'name': 'FAQ', 'url': reverse('pages:faq')},
            ],
            'services': [
                {'name': 'Business Websites', 'url': reverse('users:quote_request') + '?type=business'},
                {'name': 'E-commerce Stores', 'url': reverse('users:quote_request') + '?type=ecommerce'},
                {'name': 'Web Applications', 'url': reverse('users:quote_request') + '?type=web_app'},
                {'name': 'Portfolio Sites', 'url': reverse('users:quote_request') + '?type=portfolio'},
            ],
            'support': [
                {'name': 'Get Quote', 'url': reverse('users:quote_request')},
                {'name': 'Login', 'url': reverse('users:login')},
                {'name': 'Register', 'url': reverse('users:register')},
                {'name': 'Privacy Policy', 'url': reverse('pages:privacy')},
            ],
        },
        
        # Social media links from settings
        'social_links': settings.ONEHUX_COMPANY_INFO.get('SOCIAL_MEDIA', {}),
        
        # Quick contact info
        'contact_info': {
            'email': settings.ONEHUX_COMPANY_INFO.get('CONTACT_EMAIL'),
            'support_email': settings.ONEHUX_COMPANY_INFO.get('SUPPORT_EMAIL'),
            'phone': settings.ONEHUX_COMPANY_INFO.get('PHONE_SUPPORT'),
        },
        
        # Call-to-action buttons data
        'cta_buttons': {
            'primary': {
                'text': 'Get Free Quote',
                'url': reverse('users:quote_request'),
                'class': 'btn-primary'
            },
            'secondary': {
                'text': 'View Our Work',
                'url': '#portfolio',  # Will be implemented later
                'class': 'btn-secondary'
            }
        },
        
        # Feature highlights for homepage
        'features': [
            {
                'icon': 'rocket',
                'title': 'Fast Delivery',
                'description': 'Quick turnaround times without compromising quality'
            },
            {
                'icon': 'shield-check',
                'title': 'Secure & Reliable',
                'description': 'Built with security best practices and reliable hosting'
            },
            {
                'icon': 'device-mobile',
                'title': 'Mobile Responsive',
                'description': 'Perfectly optimized for all devices and screen sizes'
            },
            {
                'icon': 'search',
                'title': 'SEO Optimized',
                'description': 'Search engine optimized to help your business grow'
            },
            {
                'icon': 'support',
                'title': '24/7 Support',
                'description': 'Ongoing support and maintenance for your peace of mind'
            },
            {
                'icon': 'dollar',
                'title': 'Affordable Pricing',
                'description': 'Competitive pricing with no hidden fees or surprises'
            },
        ],
        
        # Testimonials (can be moved to database later)
        'testimonials': [
            {
                'name': 'Sarah Johnson',
                'company': 'Johnson Consulting',
                'text': 'Onehux Web Service delivered exactly what we needed. Professional, fast, and affordable.',
                'rating': 5,
                'image': '/static/images/testimonials/sarah-j.jpg'
            },
            {
                'name': 'Mike Chen',
                'company': 'Chen\'s Restaurant',
                'text': 'Our new website has brought in so many more customers. Thank you for the amazing work!',
                'rating': 5,
                'image': '/static/images/testimonials/mike-c.jpg'
            },
            {
                'name': 'Lisa Rodriguez',
                'company': 'Rodriguez Law Firm',
                'text': 'Professional service from start to finish. Our law firm website looks fantastic.',
                'rating': 5,
                'image': '/static/images/testimonials/lisa-r.jpg'
            },
        ],
        
        # FAQ data (can be moved to database later)
        'common_faqs': [
            {
                'question': 'How long does it take to build a website?',
                'answer': 'Typical websites take 2-4 weeks, depending on complexity and features required.'
            },
            {
                'question': 'Do you provide hosting services?',
                'answer': 'Yes, we offer reliable hosting services optimized for the websites we build.'
            },
            {
                'question': 'Can I update my website content myself?',
                'answer': 'Absolutely! We can include a user-friendly content management system.'
            },
            {
                'question': 'Do you offer ongoing support?',
                'answer': 'Yes, we provide ongoing support and maintenance packages for all our clients.'
            },
        ],
    }
    
    # Add current page info for navigation highlighting
    current_url_name = None
    if hasattr(request, 'resolver_match') and request.resolver_match:
        current_url_name = request.resolver_match.url_name
        context['current_url_name'] = current_url_name
    
    # Add user-specific context
    if request.user.is_authenticated:
        context['user_nav'] = [
            {'name': 'Dashboard', 'url': reverse('users:dashboard')},
            {'name': 'My Quotes', 'url': reverse('users:my_quotes')},
            {'name': 'Profile', 'url': reverse('users:profile')},
            {'name': 'Logout', 'url': reverse('users:logout')},
        ]
    else:
        context['user_nav'] = [
            {'name': 'Login', 'url': reverse('users:login')},
            {'name': 'Register', 'url': reverse('users:register')},
        ]
    
    # Add maintenance mode info
    context['maintenance_mode'] = getattr(settings, 'MAINTENANCE_MODE', False)
    
    # Add structured data for SEO (JSON-LD)
    context['structured_data'] = {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        'name': settings.ONEHUX_COMPANY_INFO.get('NAME'),
        'description': settings.SITE_META.get('site_description', ''),
        'url': settings.BASE_URL,
        'email': settings.ONEHUX_COMPANY_INFO.get('CONTACT_EMAIL'),
        'telephone': settings.ONEHUX_COMPANY_INFO.get('PHONE_SUPPORT'),
        'sameAs': list(settings.ONEHUX_COMPANY_INFO.get('SOCIAL_MEDIA', {}).values()),
        'address': {
            '@type': 'PostalAddress',
            'addressLocality': 'Worldwide',
            'addressCountry': 'Global'
        },
        'areaServed': 'Worldwide',
        'serviceType': 'Website Development',
        'priceRange': '$500-$10000+'
    }
    
    return context


def analytics_context(request):
    """
    Add analytics and tracking context
    """
    context = {}
    
    # Google Analytics
    ga_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', None)
    if ga_id and not settings.DEBUG:
        context['google_analytics_id'] = ga_id
    
    # Facebook Pixel
    fb_pixel_id = getattr(settings, 'FACEBOOK_PIXEL_ID', None)
    if fb_pixel_id and not settings.DEBUG:
        context['facebook_pixel_id'] = fb_pixel_id
    
    # Other tracking codes
    hotjar_id = getattr(settings, 'HOTJAR_ID', None)
    if hotjar_id and not settings.DEBUG:
        context['hotjar_id'] = hotjar_id
    
    return context


def performance_context(request):
    """
    Add performance and optimization context
    """
    context = {}
    
    # Add timestamp for cache busting in development
    if settings.DEBUG:
        context['cache_buster'] = int(timezone.now().timestamp())
    
    # Add resource hints for better performance
    context['dns_prefetch'] = [
        '//fonts.googleapis.com',
        '//www.google-analytics.com',
        '//connect.facebook.net',
    ]
    
    context['preconnect'] = [
        'https://fonts.gstatic.com',
    ]
    
    return context

