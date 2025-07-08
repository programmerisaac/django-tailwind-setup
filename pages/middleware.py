# maintenance_middleware.py
from django.shortcuts import render
from django.conf import settings

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is on
        if getattr(settings, 'MAINTENANCE_MODE', False):
            return render(request, 'maintenance.html')
        
        response = self.get_response(request)
        return response
