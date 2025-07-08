from django.urls import path
from . import views



app_name = "pages"

urlpatterns = [
	path('', views.home, name='home'),
	path('about-us/', views.about, name='about'),
	path('contact-us/', views.contact, name='contact'),
	path('terms-and-conditions/', views.terms, name='terms'),
	path('privacy-policy/', views.privacy, name='privacy'),
	path('return-policy/', views.return_policy, name='return_policy'),
	path('services/', views.services, name='services'),
	path('faq/', views.faq, name='faq'),
]
