#pages/views.py

from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

from service_providers.models import ServiceProvider


from users.email_utils import send_email_from


# from django.core.mail import send_mail


def home(request):
	context = {'page_title':''}

	# send_mail(
	# 	subject="Test Email from Django",
	# 	message="This is a test email from your Django app using Zoho.",
	# 	from_email=settings.DEFAULT_FROM_EMAIL,
	# 	recipient_list=["themporst1@gmail.com"],
	# 	fail_silently=False,
	# )

	# send_email_from(
	# 	# 'zoho_hi',
	# 	'zoho_support',
	# 	'Welcome to OneHux',
	# 	'Thank you for registering.',
	# 	['themporst1@gmail.com']
	# )


	# context['total_users'] = User.objects.filter(deleted_at__isnull=True).count()
	# context['total_services'] = ServiceProvider.objects.filter(is_active=True).count()
	return render(request, 'pages/home.html', context)



# def home(request):
# 	context = {'page_title':''}

# 	# send_mail(
# 	# 	subject="Test Email from Django",
# 	# 	message="This is a test email from your Django app using Zoho.",
# 	# 	from_email=settings.DEFAULT_FROM_EMAIL,
# 	# 	recipient_list=["themporst1@gmail.com"],
# 	# 	fail_silently=False,
# 	# )

# 	send_email_from(
# 		'zoho_support',
# 		'Welcome to OneHux',
# 		'Thank you for registering.',
# 		['newuser@example.com']
# 	)


# 	# context['total_users'] = User.objects.filter(deleted_at__isnull=True).count()
# 	# context['total_services'] = ServiceProvider.objects.filter(is_active=True).count()
# 	return render(request, 'pages/home.html', context)


# def home_view(request):
#     """
#     Home page view for Onehux Accounts
#     """
#     context = {
#         'total_users': User.objects.filter(deleted_at__isnull=True).count(),
#         'total_services': ServiceProvider.objects.filter(is_active=True).count(),
#     }
#     return render(request, 'base/home.html', context)


# def home(request):
# 	icon_classes = [
# 		"fa-sign-in-alt", "fa-shield-alt", "fa-user-circle", "fa-mobile-alt", "fa-bell", "fa-store",
# 		"fa-globe", "fa-home", "fa-cash-register", "fa-robot", "fa-download", "fa-truck", "fa-tools",
# 		"fa-paint-brush", "fa-share-alt", "fa-lock", "fa-user-shield", "fa-history", "fa-plus", "fa-cogs",
# 		"fa-link", "fa-file-signature", "fa-brain", "fa-code", "fa-laptop-code", "fa-chart-line",
# 		"fa-box", "fa-credit-card", "fa-shipping-fast", "fa-bullhorn", "fa-tags", "fa-fingerprint",
# 		"fa-shield-virus", "fa-file-invoice", "fa-headset", "fa-project-diagram", "fa-hands-helping",
# 		"fa-bug", "fa-database", "fa-terminal", "fa-network-wired", "fa-wrench", "fa-globe-africa",
# 		"fa-camera", "fa-video", "fa-lightbulb", "fa-plug", "fa-cloud", "fa-cloud-upload-alt", "fa-tasks"
# 	]
# 	icon_count = len(icon_classes)
# 	context = {
# 		'page_title':'Homepage',
# 		'icon_count':icon_count,
# 		'icon_classes':icon_classes
# 	}
	
# 	return render(request, 'pages/home.html', context)



# def home(request):
# 	context = {'page_title': 'Homepage'}
# 	context['my_value'] = request.session.get('_auth_user_id', 'default_value')
# 	# Access the session data directly
# 	# session_data = request.session.items()  # This will give you all the session data as key-value pairs
# 	# context['session'] = session_data
# 	# Set a simple key-value pair (expires in 300 seconds/5 minutes by default)
# 	# cache.set('my_key', 'my_value', timeout=300)
# 	# c = request.COOKIES.get("auth_token")
# 	# print("COOKIES ====> ", c)

# 	# # Add success message
# 	# messages.success(request, "Your changes were saved successfully!")
	
# 	# # Add error message
# 	# messages.error(request, "Something went wrong!")
	
# 	# # Add info message
# 	# messages.info(request, "Please note this important information.")
	
# 	# Add warning message
# 	# messages.warning(request, "Be careful with this operation!")
# 	icon_classes = [
# 		"fa-sign-in-alt", "fa-shield-alt", "fa-user-circle", "fa-mobile-alt", "fa-bell", "fa-store",
# 		"fa-globe", "fa-home", "fa-cash-register", "fa-robot", "fa-download", "fa-truck", "fa-tools",
# 		"fa-paint-brush", "fa-share-alt", "fa-lock", "fa-user-shield", "fa-history", "fa-plus", "fa-cogs",
# 		"fa-link", "fa-file-signature", "fa-brain", "fa-code", "fa-laptop-code", "fa-chart-line",
# 		"fa-box", "fa-credit-card", "fa-shipping-fast", "fa-bullhorn", "fa-tags", "fa-fingerprint",
# 		"fa-shield-virus", "fa-file-invoice", "fa-headset", "fa-project-diagram", "fa-hands-helping",
# 		"fa-bug", "fa-database", "fa-terminal", "fa-network-wired", "fa-wrench", "fa-globe-africa",
# 		"fa-camera", "fa-video", "fa-lightbulb", "fa-plug", "fa-cloud", "fa-cloud-upload-alt", "fa-tasks"
# 	]
# 	icon_count = len(icon_classes)
# 	context['icon_classes'] = icon_classes

# 	return render(request, 'pages/home.html', context)


def my_view(request):
	# Your view logic...
	
	# Add success message
	messages.success(request, "Your changes were saved successfully!")
	
	# Add error message
	messages.error(request, "Something went wrong!")
	
	# Add info message
	messages.info(request, "Please note this important information.")
	
	# Add warning message
	messages.warning(request, "Be careful with this operation!")
	
	return redirect('some_view')



def about(request):
	page_title = "About Us"
	context = {'page_title':page_title}
	return render(request, 'pages/about.html',context)


def contact(request):
	# if request.method == 'POST':
	# 	form = ContactForm(request.POST)
	# 	if form.is_valid():
	# 		form.save()
	# 		messages.success(request, 'Your message has been sent successfully!')
	# 		return redirect('contact_us')
	# 	else:
	# 		messages.error(request, 'There was an error sending your message. Please check the form and try again.')
	# else:
	# 	form = ContactForm()
	context = {}
	return render(request, 'pages/contact.html', context)


def privacy(request):
	page_title = "Privacy Policy"
	context = {'page_title':page_title}
	return render(request, 'pages/privacy.html',context)

def terms(request):
	page_title = "Terms and Conditions"
	context = {'page_title':page_title}
	return render(request, 'pages/terms.html',context)

def return_policy(request):
	page_title = "Return Policy"
	context = {'page_title':page_title}
	return render(request, 'pages/return_policy.html',context)

def services(request):
	page_title = "Services "
	context = {'page_title':page_title}
	return render(request, 'pages/services.html',context)


def contact(request):
	page_title = "Contact "
	context = {'page_title':page_title}
	return render(request, 'pages/contact.html',context)


def faq(request):
	page_title = "Faq "
	context = {'page_title':page_title}
	return render(request, 'pages/faq.html',context)

