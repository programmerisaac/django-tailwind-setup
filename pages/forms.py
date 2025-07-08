# from django import forms
# from .models import Contact

# class ContactForm(forms.ModelForm):
#     class Meta:
#         model = Contact
#         fields = ['full_name', 'email', 'phone_number', 'subject', 'message']
#         widgets = {
#             'full_name': forms.TextInput(attrs={'class': 'input','placeholder': 'Full Name'}),
#             'email': forms.EmailInput(attrs={'class': 'input','placeholder': 'Email'}),
#             'phone_number': forms.TextInput(attrs={'class': 'input','placeholder': 'Phone Number'}),
#             'subject': forms.TextInput(attrs={'class': 'input','placeholder': 'Subject'}),
#             'message': forms.Textarea(attrs={'class': 'input','placeholder': 'Message'}),
#         }

#         labels = {
#             'full_name': '',
#             'phone_number': '',
#             'email': '',
#             'address': '',
#             'subject': '',
#             'message': '',
#         }
