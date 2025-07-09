# users/forms.py
"""
Forms for user authentication and website quote system
=====================================================
Django forms with validation and styling for user registration, 
login, profile management, and quote requests.

Author: Isaac
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

from .models import User, WebsiteQuote, Newsletter


class BaseForm:
    """Base form class with common styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_base_styling()
    
    def apply_base_styling(self):
        """Apply Tailwind CSS classes to form fields"""
        for field_name, field in self.fields.items():
            # Base classes for all inputs
            base_classes = (
                "w-full px-4 py-3 rounded-lg border border-gray-300 "
                "focus:border-primary focus:ring-2 focus:ring-primary/20 "
                "focus:outline-none transition-all duration-200 "
                "placeholder-gray-500"
            )
            
            # Error state classes
            error_classes = (
                "border-red-500 focus:border-red-500 "
                "focus:ring-red-500/20"
            )
            
            # Special handling for different field types
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': (
                        "w-4 h-4 text-primary bg-gray-100 border-gray-300 "
                        "rounded focus:ring-primary focus:ring-2"
                    )
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': (
                        base_classes + " "
                        "bg-white cursor-pointer"
                    )
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': base_classes,
                    'rows': 4
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    'class': (
                        "w-full px-4 py-3 rounded-lg border border-gray-300 "
                        "focus:border-primary focus:ring-2 focus:ring-primary/20 "
                        "focus:outline-none transition-all duration-200 "
                        "file:mr-4 file:py-2 file:px-4 file:rounded-lg "
                        "file:border-0 file:bg-primary file:text-white "
                        "file:hover:bg-primary/90 file:cursor-pointer"
                    )
                })
            else:
                field.widget.attrs.update({
                    'class': base_classes
                })
            
            # Add placeholder if not already present
            if hasattr(field.widget, 'attrs') and 'placeholder' not in field.widget.attrs:
                if field.label:
                    field.widget.attrs['placeholder'] = f"Enter {field.label.lower()}"


class UserRegistrationForm(BaseForm, UserCreationForm):
    """
    Enhanced user registration form with additional fields
    """
    
    email = forms.EmailField(
        label=_("Email Address"),
        help_text=_("We'll use this for your account login"),
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        label=_("First Name"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Your first name',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        label=_("Last Name"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Your last name',
            'autocomplete': 'family-name'
        })
    )
    
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        label=_("Phone Number"),
        help_text=_("Optional - for project communication"),
        widget=forms.TextInput(attrs={
            'placeholder': '+1 (555) 123-4567',
            'autocomplete': 'tel'
        })
    )
    
    company_name = forms.CharField(
        max_length=255,
        required=False,
        label=_("Company Name"),
        help_text=_("Optional - if this is for business"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Your company name',
            'autocomplete': 'organization'
        })
    )
    
    newsletter_subscription = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Subscribe to our newsletter"),
        help_text=_("Get web development tips and project updates")
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label=_("I agree to the Terms and Conditions"),
        error_messages={
            'required': _("You must accept the terms and conditions to register.")
        }
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'company_name', 'password1', 'password2',
            'newsletter_subscription', 'terms_accepted'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
        
        # Customize username field
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        })
        
        # Update help texts
        self.fields['username'].help_text = _("Letters, digits and @/./+/-/_ only.")
        self.fields['password1'].help_text = _(
            "Your password should be at least 8 characters long and contain "
            "a mix of letters, numbers, and symbols."
        )
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove spaces and special characters for validation
            phone_digits = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^\+?1?\d{9,15}$', phone_digits):
                raise ValidationError(_("Please enter a valid phone number."))
        return phone
    
    def save(self, commit=True):
        """Save user with additional fields"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.company_name = self.cleaned_data.get('company_name', '')
        user.newsletter_subscription = self.cleaned_data.get('newsletter_subscription', True)
        
        if commit:
            user.save()
        return user


class UserLoginForm(BaseForm, AuthenticationForm):
    """
    Enhanced login form with email-based authentication
    """
    
    username = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your password',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Keep me logged in")
    )
    
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        # Update field order
        self.fields = {
            'username': self.fields['username'],
            'password': self.fields['password'],
            'remember_me': self.fields['remember_me'],
        }
    
    def clean(self):
        """Custom authentication using email"""
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            
            if self.user_cache is None:
                raise ValidationError(
                    _("Please enter a correct email and password."),
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class UserProfileForm(BaseForm, forms.ModelForm):
    """
    Form for updating user profile information
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'company_name', 'website', 'bio', 'avatar',
            'newsletter_subscription'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://yourwebsite.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make email readonly if user exists
        if self.instance and self.instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].help_text = _(
                "Contact support to change your email address"
            )


class WebsiteQuoteForm(BaseForm, forms.ModelForm):
    """
    Form for website development quote requests
    """
    
    # Additional fields not in the model
    additional_features = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ('cms', _('Content Management System')),
            ('ecommerce', _('E-commerce Integration')),
            ('booking', _('Booking/Appointment System')),
            ('payment', _('Payment Gateway')),
            ('membership', _('User Membership')),
            ('api', _('Third-party API Integration')),
            ('mobile_app', _('Mobile App Companion')),
            ('seo', _('Advanced SEO Package')),
            ('analytics', _('Analytics Dashboard')),
            ('social', _('Social Media Integration')),
        ],
        label=_("Additional Features"),
        help_text=_("Select any additional features you need")
    )
    
    inspiration_websites = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label=_("Inspiration Websites"),
        help_text=_("Share URLs of websites you like or want to emulate")
    )
    
    class Meta:
        model = WebsiteQuote
        fields = [
            'full_name', 'email', 'phone', 'company_name',
            'website_type', 'project_description', 'budget_range',
            'timeline', 'current_website', 'additional_features',
            'inspiration_websites'
        ]
        widgets = {
            'project_description': forms.Textarea(attrs={'rows': 5}),
            'current_website': forms.URLInput(attrs={
                'placeholder': 'https://yourcurrentsite.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add dynamic cost estimation
        self.fields['website_type'].widget.attrs.update({
            'x-on:change': 'updateEstimate()'
        })
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_digits = re.sub(r'[^\d+]', '', phone)
            if not re.match(r'^\+?1?\d{9,15}$', phone_digits):
                raise ValidationError(_("Please enter a valid phone number."))
        return phone
    
    def save(self, commit=True):
        """Save quote with additional features"""
        quote = super().save(commit=False)
        
        # Save additional features as JSON
        additional_features = self.cleaned_data.get('additional_features', [])
        quote.features_needed = additional_features
        
        if commit:
            quote.save()
        return quote


class NewsletterForm(BaseForm, forms.ModelForm):
    """
    Simple newsletter subscription form
    """
    
    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Your name (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False


class ContactForm(BaseForm, forms.Form):
    """
    General contact form
    """
    
    name = forms.CharField(
        max_length=255,
        label=_("Your Name"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your full name'
        })
    )
    
    email = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com'
        })
    )
    
    subject = forms.CharField(
        max_length=255,
        label=_("Subject"),
        widget=forms.TextInput(attrs={
            'placeholder': 'What is this about?'
        })
    )
    
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={
            'placeholder': 'Tell us how we can help you...',
            'rows': 6
        })
    )
    
    def send_email(self):
        """Send contact form email"""
        # This would integrate with your email backend
        pass
