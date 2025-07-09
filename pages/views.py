# pages/views.py
"""
Views for pages app - main website pages
========================================
Handles static pages like home, about, contact, services, etc.
Includes SEO optimization and error handlers.

Author: Isaac
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
import json
import logging

from users.models import WebsiteQuote, Newsletter
from users.forms import ContactForm, NewsletterForm

logger = logging.getLogger(__name__)


# ============================================================================
# MAIN WEBSITE PAGES
# ============================================================================

# @cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    """
    Homepage - Main landing page for Onehux Web Service
    """
    # Get some statistics for the homepage
    total_projects = WebsiteQuote.objects.filter(status='completed').count()
    active_projects = WebsiteQuote.objects.filter(status__in=['approved', 'in_progress']).count()
    
    # Popular website types
    popular_types = WebsiteQuote.objects.values('website_type').annotate(
        count=Count('website_type')
    ).order_by('-count')[:3]
    
    # SEO metadata
    page_title = "Professional Website Development Services - Onehux Web Service"
    meta_description = ("Transform your business with custom websites. Professional web development "
                       "services for businesses, e-commerce, portfolios, and web applications. "
                       "Get a free quote today!")
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'meta_keywords': 'website development, web design, business websites, e-commerce development, professional web services',
        'canonical_url': f"{settings.BASE_URL}/",
        'og_title': page_title,
        'og_description': meta_description,
        'og_image': f"{settings.BASE_URL}/static/images/og-home.jpg",
        
        # Statistics
        'stats': {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'popular_types': popular_types,
            'years_experience': 5,
            'happy_clients': total_projects + 50,  # Adding some base number
        },
        
        # Services showcase
        'featured_services': [
            {
                'title': 'Business Websites',
                'description': 'Professional websites that establish credibility and drive growth.',
                'icon': 'building-office',
                'price_from': '$1,200',
                'features': ['Custom Design', 'Mobile Responsive', 'SEO Optimized', 'Contact Forms'],
                'url': '/quote/?type=business'
            },
            {
                'title': 'E-commerce Stores', 
                'description': 'Complete online stores with payment processing and inventory management.',
                'icon': 'shopping-cart',
                'price_from': '$2,500',
                'features': ['Product Catalog', 'Payment Gateway', 'Order Management', 'Analytics'],
                'url': '/quote/?type=ecommerce'
            },
            {
                'title': 'Web Applications',
                'description': 'Custom web applications tailored to your specific business needs.',
                'icon': 'computer-desktop',
                'price_from': '$3,500',
                'features': ['Custom Features', 'User Management', 'API Integration', 'Scalable'],
                'url': '/quote/?type=web_app'
            },
        ],
        
        # Process steps
        'process_steps': [
            {
                'step': 1,
                'title': 'Consultation',
                'description': 'We discuss your requirements and create a detailed project plan.',
                'icon': 'chat-bubble-left-right'
            },
            {
                'step': 2,
                'title': 'Design & Development',
                'description': 'Our team creates your custom website with regular progress updates.',
                'icon': 'code-bracket'
            },
            {
                'step': 3,
                'title': 'Testing & Launch',
                'description': 'Thorough testing ensures everything works perfectly before launch.',
                'icon': 'rocket-launch'
            },
            {
                'step': 4,
                'title': 'Ongoing Support',
                'description': 'We provide continuous support and maintenance for your website.',
                'icon': 'wrench-screwdriver'
            },
        ],
        
        # Trust indicators
        'trust_indicators': [
            {'icon': 'shield-check', 'text': 'SSL Secure'},
            {'icon': 'clock', 'text': 'Fast Delivery'},
            {'icon': 'currency-dollar', 'text': 'Money Back Guarantee'},
            {'icon': 'phone', 'text': '24/7 Support'},
        ],
    }
    
    return render(request, 'pages/home.html', context)


def about(request):
    """About page with company information"""
    page_title = "About Onehux Web Service - Expert Web Development Team"
    meta_description = ("Learn about Onehux Web Service, your trusted partner for professional website development. "
                       "Experienced team delivering custom web solutions for businesses worldwide.")
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/about/",
        
        # Team values
        'values': [
            {
                'title': 'Quality First',
                'description': 'We never compromise on quality. Every website is built to the highest standards.',
                'icon': 'star'
            },
            {
                'title': 'Client Success',
                'description': 'Your success is our success. We work until you are completely satisfied.',
                'icon': 'trophy'
            },
            {
                'title': 'Innovation',
                'description': 'We stay updated with the latest technologies and design trends.',
                'icon': 'light-bulb'
            },
            {
                'title': 'Reliability',
                'description': 'Dependable service delivery and ongoing support you can count on.',
                'icon': 'shield-check'
            },
        ],
        
        # Skills/Technologies
        'technologies': [
            {'name': 'Django', 'proficiency': 95},
            {'name': 'React', 'proficiency': 90},
            {'name': 'PostgreSQL', 'proficiency': 92},
            {'name': 'Tailwind CSS', 'proficiency': 88},
            {'name': 'AWS/Cloud', 'proficiency': 85},
            {'name': 'SEO', 'proficiency': 90},
        ],
    }
    
    return render(request, 'pages/about.html', context)


def services(request):
    """Services page detailing all offerings"""
    page_title = "Web Development Services - Custom Websites & Applications"
    meta_description = ("Comprehensive web development services including business websites, e-commerce stores, "
                       "web applications, and custom solutions. View our full service portfolio.")
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/services/",
        
        # Detailed services
        'services': [
            {
                'category': 'Business Websites',
                'services': [
                    {
                        'name': 'Corporate Website',
                        'description': 'Professional websites for established businesses',
                        'price_range': '$1,200 - $3,000',
                        'timeline': '2-3 weeks',
                        'features': ['Custom Design', 'CMS', 'Contact Forms', 'SEO Setup']
                    },
                    {
                        'name': 'Small Business Site',
                        'description': 'Perfect starter websites for small businesses',
                        'price_range': '$800 - $1,500',
                        'timeline': '1-2 weeks',
                        'features': ['Template Customization', 'Basic SEO', 'Contact Info']
                    },
                    {
                        'name': 'Landing Page',
                        'description': 'High-converting single page websites',
                        'price_range': '$500 - $1,000',
                        'timeline': '3-5 days',
                        'features': ['Call-to-Action', 'Lead Capture', 'Analytics']
                    },
                ]
            },
            {
                'category': 'E-commerce Solutions',
                'services': [
                    {
                        'name': 'Online Store',
                        'description': 'Complete e-commerce websites with payment processing',
                        'price_range': '$2,500 - $5,000',
                        'timeline': '3-4 weeks',
                        'features': ['Product Catalog', 'Shopping Cart', 'Payment Gateway', 'Inventory']
                    },
                    {
                        'name': 'Marketplace Integration',
                        'description': 'Connect your store with Amazon, eBay, etc.',
                        'price_range': '$1,000 - $2,000',
                        'timeline': '1-2 weeks',
                        'features': ['API Integration', 'Sync Products', 'Order Management']
                    },
                ]
            },
            {
                'category': 'Web Applications',
                'services': [
                    {
                        'name': 'Custom Web App',
                        'description': 'Tailored applications for specific business needs',
                        'price_range': '$3,500 - $10,000+',
                        'timeline': '4-8 weeks',
                        'features': ['Custom Features', 'User Management', 'Database', 'API']
                    },
                    {
                        'name': 'SaaS Platform',
                        'description': 'Software-as-a-Service platforms with subscriptions',
                        'price_range': '$5,000 - $15,000+',
                        'timeline': '6-12 weeks',
                        'features': ['Multi-tenant', 'Billing', 'Analytics', 'Scalable']
                    },
                ]
            },
        ],
        
        # Add-on services
        'addons': [
            {'name': 'SEO Package', 'price': '$200-500', 'description': 'Complete SEO optimization'},
            {'name': 'Hosting Setup', 'price': '$100-300', 'description': 'Professional hosting configuration'},
            {'name': 'Maintenance Plan', 'price': '$50-200/month', 'description': 'Ongoing updates and support'},
            {'name': 'Analytics Setup', 'price': '$150', 'description': 'Google Analytics and tracking'},
        ],
    }
    
    return render(request, 'pages/services.html', context)


def contact(request):
    """Contact page with form and company information"""
    page_title = "Contact Onehux Web Service - Get Your Free Consultation"
    meta_description = ("Contact Onehux Web Service for professional website development. "
                       "Get a free consultation and quote for your next web project.")
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process contact form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email notification
            try:
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=f'From: {name} <{email}>\n\nMessage:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL']],
                    fail_silently=False,
                )
                
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('pages:contact')
                
            except Exception as e:
                logger.error(f'Failed to send contact email: {e}')
                messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/contact/",
        'form': form,
        
        # Contact methods
        'contact_methods': [
            {
                'icon': 'envelope',
                'title': 'Email Us',
                'value': settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL'],
                'action': f"mailto:{settings.ONEHUX_COMPANY_INFO['CONTACT_EMAIL']}"
            },
            {
                'icon': 'phone',
                'title': 'Call Us',
                'value': settings.ONEHUX_COMPANY_INFO['PHONE_SUPPORT'],
                'action': f"tel:{settings.ONEHUX_COMPANY_INFO['PHONE_SUPPORT']}"
            },
            {
                'icon': 'chat-bubble-left-right',
                'title': 'Get Quote',
                'value': 'Free Consultation',
                'action': '/quote/'
            },
        ],
        
        # Business hours
        'business_hours': [
            {'day': 'Monday - Friday', 'hours': '9:00 AM - 6:00 PM'},
            {'day': 'Saturday', 'hours': '10:00 AM - 4:00 PM'},
            {'day': 'Sunday', 'hours': 'Closed'},
        ],
    }
    
    return render(request, 'pages/contact.html', context)


def faq(request):
    """FAQ page with common questions and answers"""
    page_title = "Frequently Asked Questions - Web Development Services"
    meta_description = ("Find answers to common questions about our web development services, "
                       "pricing, timelines, and support options.")
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/faq/",
        
        # FAQ categories
        'faq_categories': [
            {
                'category': 'General Services',
                'questions': [
                    {
                        'question': 'What types of websites do you build?',
                        'answer': 'We build all types of websites including business websites, e-commerce stores, portfolios, blogs, landing pages, and custom web applications.'
                    },
                    {
                        'question': 'How long does it take to build a website?',
                        'answer': 'Timeline depends on complexity. Simple websites take 1-2 weeks, business sites 2-4 weeks, and complex applications 4-8 weeks or more.'
                    },
                    {
                        'question': 'Do you provide website hosting?',
                        'answer': 'Yes, we offer reliable hosting services optimized for the websites we build, with 99.9% uptime guarantee.'
                    },
                ]
            },
            {
                'category': 'Pricing & Payment',
                'questions': [
                    {
                        'question': 'How much does a website cost?',
                        'answer': 'Costs vary based on requirements. Simple sites start at $500, business websites from $1,200, and e-commerce from $2,500. Get a free quote for accurate pricing.'
                    },
                    {
                        'question': 'Do you require full payment upfront?',
                        'answer': 'No, we typically work with a 50% deposit to start and 50% upon completion. For larger projects, we can arrange milestone payments.'
                    },
                    {
                        'question': 'What payment methods do you accept?',
                        'answer': 'We accept bank transfers, credit cards, PayPal, and other secure payment methods.'
                    },
                ]
            },
            {
                'category': 'Technical Questions',
                'questions': [
                    {
                        'question': 'Will my website be mobile-friendly?',
                        'answer': 'Absolutely! All our websites are fully responsive and optimized for mobile devices, tablets, and desktops.'
                    },
                    {
                        'question': 'Do you provide SEO services?',
                        'answer': 'Yes, basic SEO is included with all websites. We also offer advanced SEO packages for better search engine rankings.'
                    },
                    {
                        'question': 'Can I update my website content myself?',
                        'answer': 'Yes, we can include a user-friendly content management system (CMS) that allows you to easily update your website content.'
                    },
                ]
            },
            {
                'category': 'Support & Maintenance',
                'questions': [
                    {
                        'question': 'Do you provide ongoing support?',
                        'answer': 'Yes, we offer various support and maintenance packages to keep your website updated, secure, and running smoothly.'
                    },
                    {
                        'question': 'What if I need changes after the website is live?',
                        'answer': 'Minor changes are included for the first month. Additional changes can be made as part of our maintenance plans or on an hourly basis.'
                    },
                    {
                        'question': 'Do you provide training on how to use my website?',
                        'answer': 'Yes, we provide comprehensive training on how to manage and update your website, including video tutorials and documentation.'
                    },
                ]
            },
        ],
    }
    
    return render(request, 'pages/faq.html', context)


def privacy(request):
    """Privacy policy page"""
    page_title = "Privacy Policy - Onehux Web Service"
    meta_description = "Privacy policy for Onehux Web Service detailing how we collect, use, and protect your personal information."
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/privacy/",
        'last_updated': '2025-01-01',  # Update this when you change the policy
    }
    
    return render(request, 'pages/privacy.html', context)


def terms(request):
    """Terms and conditions page"""
    page_title = "Terms and Conditions - Onehux Web Service"
    meta_description = "Terms and conditions for using Onehux Web Service website development services."
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/terms/",
        'last_updated': '2025-01-01',  # Update this when you change the terms
    }
    
    return render(request, 'pages/terms.html', context)


def return_policy(request):
    """Return/refund policy page"""
    page_title = "Return Policy - Onehux Web Service"
    meta_description = "Return and refund policy for Onehux Web Service website development services."
    
    context = {
        'page_title': page_title,
        'meta_description': meta_description,
        'canonical_url': f"{settings.BASE_URL}/return-policy/",
        'last_updated': '2025-01-01',
    }
    
    return render(request, 'pages/return_policy.html', context)


# ============================================================================
# AJAX ENDPOINTS
# ============================================================================

@require_http_methods(["POST"])
@csrf_exempt
def quick_newsletter_signup(request):
    """Quick newsletter signup via AJAX"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to our newsletter!'
            })
        else:
            if newsletter.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'You are already subscribed.'
                })
            else:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! Subscription reactivated.'
                })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid data'})
    except Exception as e:
        logger.error(f'Newsletter signup error: {e}')
        return JsonResponse({'success': False, 'message': 'An error occurred'})


# ============================================================================
# ERROR HANDLERS
# ============================================================================

def bad_request(request, exception):
    """Custom 400 error handler"""
    context = {
        'page_title': '400 - Bad Request',
        'error_code': '400',
        'error_title': 'Bad Request',
        'error_message': 'Sorry, your request could not be processed.',
    }
    return render(request, 'errors/error.html', context, status=400)


def permission_denied(request, exception):
    """Custom 403 error handler"""
    context = {
        'page_title': '403 - Permission Denied',
        'error_code': '403',
        'error_title': 'Permission Denied',
        'error_message': 'Sorry, you do not have permission to access this page.',
    }
    return render(request, 'errors/error.html', context, status=403)


def page_not_found(request, exception):
    """Custom 404 error handler"""
    context = {
        'page_title': '404 - Page Not Found',
        'error_code': '404',
        'error_title': 'Page Not Found',
        'error_message': 'Sorry, the page you are looking for could not be found.',
    }
    return render(request, 'errors/404.html', context, status=404)


def server_error(request):
    """Custom 500 error handler"""
    context = {
        'page_title': '500 - Server Error',
        'error_code': '500',
        'error_title': 'Server Error',
        'error_message': 'Sorry, something went wrong on our end. Please try again later.',
    }
    return render(request, 'errors/error.html', context, status=500)














# from django.shortcuts import render,redirect
# from django.views.decorators.cache import cache_page
# from django.contrib import messages
# import logging
# from users.models import WebsiteQuote


# logger = logging.getLogger(__name__)

# # ============================================================================
# # HOME & LANDING PAGE VIEWS
# # ============================================================================

# @cache_page(60 * 15)  # Cache for 15 minutes
# def home(request):
#     """
#     Main landing page for Onehux Web Service
#     Showcases services and captures leads
#     """
#     page_title = "Professional Website Development Services - Onehux"
#     meta_description = ("Transform your business with custom websites. Professional web development "
#                        "services for businesses, e-commerce, portfolios, and web applications. Get a free quote today!")
    
#     # Get recent testimonials or featured work (if you add them later)
#     recent_quotes_count = WebsiteQuote.objects.filter(status='completed').count()
    
#     context = {
#         'page_title': page_title,
#         'meta_description': meta_description,
#         'recent_quotes_count': recent_quotes_count,
#         'services': [
#             {
#                 'title': 'Business Websites',
#                 'description': 'Professional websites that establish your online presence and build credibility.',
#                 'icon': 'building-office',
#                 'features': ['Responsive Design', 'SEO Optimized', 'Fast Loading', 'Mobile Friendly']
#             },
#             {
#                 'title': 'E-commerce Stores',
#                 'description': 'Complete online stores with payment integration and inventory management.',
#                 'icon': 'shopping-cart',
#                 'features': ['Payment Gateway', 'Product Catalog', 'Order Management', 'Analytics']
#             },
#             {
#                 'title': 'Web Applications',
#                 'description': 'Custom web applications tailored to your specific business needs.',
#                 'icon': 'computer-desktop',
#                 'features': ['Custom Features', 'User Management', 'Database Integration', 'API Development']
#             },
#             {
#                 'title': 'Portfolio Websites',
#                 'description': 'Showcase your work and attract clients with stunning portfolio sites.',
#                 'icon': 'photo',
#                 'features': ['Gallery System', 'Contact Forms', 'Social Integration', 'Blog Support']
#             }
#         ]
#     }
    
#     return render(request, 'pages/home.html', context)


# def about(request):
#     """About page with company information"""
#     page_title = "About Onehux Web Service - Expert Web Development Team"
#     meta_description = ("Learn about Onehux Web Service, your trusted partner for professional website development. "
#                        "Experienced team delivering custom web solutions for businesses worldwide.")
    
#     context = {
#         'page_title': page_title,
#         'meta_description': meta_description,
#     }
    
#     return render(request, 'pages/about.html', context)


# def contact(request):
#     """Contact page with multiple contact options"""
#     page_title = "Contact Onehux Web Service - Get Your Free Quote"
#     meta_description = ("Contact Onehux Web Service for professional website development. "
#                        "Get a free consultation and quote for your next web project.")
    
#     if request.method == 'POST':
#         # Handle contact form submission
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         message = request.POST.get('message')
        
#         if name and email and message:
#             # Here you could save to a ContactMessage model or send email directly
#             messages.success(request, 'Thank you for your message! We will get back to you soon.')
#             return redirect('pages:contact')
#         else:
#             messages.error(request, 'Please fill in all required fields.')
    
#     context = {
#         'page_title': page_title,
#         'meta_description': meta_description,
#     }
    
#     return render(request, 'pages/contact.html', context)



# #################################################################################################################
# #################################################################################################################
# #################################################################################################################







