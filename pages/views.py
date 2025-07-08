#pages/views.py

from django.shortcuts import render,redirect,get_object_or_404

def home(request):
	page_title = "Home"
	context = {'page_title':page_title}
	return render(request, 'pages/home.html',context)

def about(request):
	page_title = "About"
	context = {'page_title':page_title}
	return render(request, 'pages/about.html',context)

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

