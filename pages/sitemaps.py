# pages/sitemaps.py
"""
Sitemaps for SEO optimization
============================
Generates XML sitemaps for search engines to crawl the website.

Author: Isaac
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import datetime


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages
    """
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'
    
    def items(self):
        """Return list of static page URL names"""
        return [
            'pages:home',
            'pages:about', 
            'pages:services',
            'pages:contact',
            'pages:faq',
            'pages:privacy',
            'pages:terms',
            'users:quote_request',
            'users:register',
            'users:login',
        ]
    
    def location(self, item):
        """Return the URL for each item"""
        return reverse(item)
    
    def lastmod(self, item):
        """Return last modification date"""
        # You can customize this based on when each page was last updated
        return timezone.now().date()
    
    def priority(self, item):
        """Return priority for each page"""
        priorities = {
            'pages:home': 1.0,
            'pages:services': 0.9,
            'users:quote_request': 0.9,
            'pages:about': 0.8,
            'pages:contact': 0.8,
            'users:register': 0.7,
            'users:login': 0.6,
            'pages:faq': 0.6,
            'pages:privacy': 0.3,
            'pages:terms': 0.3,
        }
        return priorities.get(item, 0.5)
    
    def changefreq(self, item):
        """Return change frequency for each page"""
        frequencies = {
            'pages:home': 'daily',
            'pages:services': 'weekly',
            'users:quote_request': 'weekly',
            'pages:about': 'monthly',
            'pages:contact': 'monthly',
            'pages:faq': 'monthly',
            'users:register': 'yearly',
            'users:login': 'yearly',
            'pages:privacy': 'yearly',
            'pages:terms': 'yearly',
        }
        return frequencies.get(item, 'monthly')


class PagesSitemap(Sitemap):
    """
    Sitemap for dynamic pages (if you add a blog or portfolio later)
    """
    priority = 0.7
    changefreq = 'weekly'
    protocol = 'https'
    
    def items(self):
        """Return dynamic page items"""
        # This is a placeholder for when you add blog posts, portfolio items, etc.
        # For now, return empty list
        return []
    
    def location(self, item):
        """Return URL for dynamic items"""
        # Implement based on your dynamic content models
        pass
    
    def lastmod(self, item):
        """Return last modification date for dynamic items"""
        # Implement based on your dynamic content models
        pass


class ServicesSitemap(Sitemap):
    """
    Sitemap for individual service pages
    """
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'
    
    def items(self):
        """Return service types for individual pages"""
        return [
            'business',
            'ecommerce', 
            'portfolio',
            'blog',
            'landing',
            'web_app',
            'custom',
        ]
    
    def location(self, item):
        """Return URL for each service type"""
        return f'/services/{item}/'
    
    def lastmod(self, item):
        """Return last modification date"""
        return timezone.now().date()
    
    def priority(self, item):
        """Return priority for each service"""
        priorities = {
            'business': 0.9,
            'ecommerce': 0.9,
            'web_app': 0.8,
            'portfolio': 0.7,
            'landing': 0.7,
            'blog': 0.6,
            'custom': 0.8,
        }
        return priorities.get(item, 0.7)
    
