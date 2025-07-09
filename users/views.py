# users/views.py
"""
Views for user authentication and website quote system
=====================================================
Handles user registration, login, profile management, and quote requests.

Author: Isaac
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
import json
import logging
from django.http import HttpResponse

from .models import User, WebsiteQuote, Newsletter
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    UserProfileForm,
    WebsiteQuoteForm,
    NewsletterForm
)
from .tasks import send_quote_email, send_welcome_email

logger = logging.getLogger(__name__)




# ============================================================================
# USER AUTHENTICATION VIEWS
# ============================================================================

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email asynchronously
            send_welcome_email.delay(user.id)
            
            # Log the user in
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f'Welcome {user.get_full_name()}! Your account has been created.')
                return redirect('users:dashboard')
            
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Create Your Account - Onehux',
    }
    
    return render(request, 'users/register.html', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Update last login IP
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save(update_fields=['last_login_ip'])
            
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            
            # Redirect to next URL or dashboard
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login to Your Account - Onehux',
    }
    
    return render(request, 'users/login.html', context)


@login_required
def logout_view(request):
    """User logout view"""
    user_name = request.user.get_full_name()
    logout(request)
    messages.success(request, f'Goodbye {user_name}! You have been logged out.')
    return redirect('pages:home')


# ============================================================================
# USER DASHBOARD & PROFILE VIEWS
# ============================================================================

@login_required
def dashboard(request):
    """User dashboard with overview of quotes and activity"""
    user_quotes = WebsiteQuote.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).order_by('-created_at')[:5]
    
    # Statistics
    total_quotes = user_quotes.count()
    active_projects = user_quotes.filter(status__in=['approved', 'in_progress']).count()
    completed_projects = user_quotes.filter(status='completed').count()
    
    context = {
        'page_title': 'Dashboard - Onehux',
        'user_quotes': user_quotes,
        'stats': {
            'total_quotes': total_quotes,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
        }
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """User profile view and edit"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'My Profile - Onehux',
    }
    
    return render(request, 'users/profile.html', context)


# ============================================================================
# WEBSITE QUOTE VIEWS
# ============================================================================

def quote_request(request):
    """Website quote request form"""
    if request.method == 'POST':
        form = WebsiteQuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            
            # Associate with user if logged in
            if request.user.is_authenticated:
                quote.user = request.user
            
            quote.save()
            
            # Send quote email asynchronously
            send_quote_email.delay(quote.id)
            
            messages.success(
                request, 
                'Thank you for your quote request! We will review your requirements and get back to you within 24 hours.'
            )
            return redirect('users:quote_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WebsiteQuoteForm()
        
        # Pre-fill form if user is logged in
        if request.user.is_authenticated:
            form.initial = {
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'phone': request.user.phone_number,
                'company_name': request.user.company_name,
                'current_website': request.user.website,
            }
    
    context = {
        'form': form,
        'page_title': 'Get Your Website Quote - Onehux',
        'meta_description': 'Get a personalized quote for your website development project. Free consultation and competitive pricing.',
    }
    
    return render(request, 'users/quote_request.html', context)


def quote_success(request):
    """Quote request success page"""
    context = {
        'page_title': 'Quote Request Submitted - Onehux',
    }
    return render(request, 'users/quote_success.html', context)


@login_required
def my_quotes(request):
    """Display user's quote requests"""
    quotes = WebsiteQuote.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(quotes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'My Quote Requests - Onehux',
    }
    
    return render(request, 'users/my_quotes.html', context)


@login_required
def quote_detail(request, pk):
    """Detailed view of a specific quote request"""
    quote = get_object_or_404(
        WebsiteQuote,
        pk=pk,
        user=request.user
    )
    
    context = {
        'quote': quote,
        'page_title': f'Quote #{quote.pk} - Onehux',
    }
    
    return render(request, 'users/quote_detail.html', context)


# ============================================================================
# AJAX & API VIEWS
# ============================================================================

@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """AJAX endpoint for newsletter subscription"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name', '')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        
        if created:
            return JsonResponse({
                'success': True, 
                'message': 'Thank you for subscribing to our newsletter!'
            })
        else:
            if newsletter.is_active:
                return JsonResponse({
                    'success': False, 
                    'message': 'You are already subscribed to our newsletter.'
                })
            else:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Welcome back! Your subscription has been reactivated.'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid data format'})
    except Exception as e:
        logger.error(f"Newsletter subscription error: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'})


@require_http_methods(["GET"])
def estimate_cost(request):
    """AJAX endpoint to provide cost estimates based on project type"""
    website_type = request.GET.get('type')
    features = request.GET.getlist('features[]')
    
    # Base costs for different website types
    base_costs = {
        'business': 1200,
        'ecommerce': 2500,
        'portfolio': 800,
        'blog': 600,
        'landing': 500,
        'web_app': 3500,
        'custom': 2000,
    }
    
    # Additional feature costs
    feature_costs = {
        'cms': 300,
        'ecommerce': 800,
        'booking': 500,
        'payment': 400,
        'membership': 600,
        'api': 800,
        'mobile_app': 1500,
        'seo': 200,
        'analytics': 150,
        'social': 100,
    }
    
    base_cost = base_costs.get(website_type, 1000)
    additional_cost = sum(feature_costs.get(feature, 0) for feature in features)
    
    total_estimate = base_cost + additional_cost
    
    return JsonResponse({
        'base_cost': base_cost,
        'additional_cost': additional_cost,
        'total_estimate': total_estimate,
        'formatted_estimate': f"${total_estimate:,}"
    })


# ============================================================================
# UTILITY VIEWS
# ============================================================================

def service_worker(request):
    """Service worker for PWA functionality"""
    return render(request, 'sw.js', content_type='application/javascript')


def robots_txt(request):
    """Robots.txt for SEO"""
    lines = [
        "User-Agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


