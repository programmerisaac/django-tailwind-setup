# pages/urls.py
"""
URL configuration for pages app
==============================
Static pages like home, about, contact, services, etc.

Author: Isaac
"""

from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    # ========================================================================
    # MAIN PAGES
    # ========================================================================
    
    # Homepage
    path('', views.home, name='home'),
    
    # Company Pages
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    
    # Legal Pages
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-and-conditions/', views.terms, name='terms'),
    path('return-policy/', views.return_policy, name='return_policy'),
    
    # ========================================================================
    # AJAX ENDPOINTS
    # ========================================================================
    
    # Newsletter signup
    path('api/newsletter/subscribe/', views.quick_newsletter_signup, name='quick_newsletter_signup'),
]




# from django.urls import path
# from . import views



# app_name = "pages"

# urlpatterns = [
# 	path('', views.home, name='home'),
# 	path('about-us/', views.about, name='about'),
# 	path('contact-us/', views.contact, name='contact'),
# 	path('terms-and-conditions/', views.terms, name='terms'),
# 	path('privacy-policy/', views.privacy, name='privacy'),
# 	path('return-policy/', views.return_policy, name='return_policy'),
# 	path('services/', views.services, name='services'),
# 	path('faq/', views.faq, name='faq'),
# ]
