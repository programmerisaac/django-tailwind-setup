# from django.db import models
# from validators.phone import phone_regex

# class Contact(models.Model):
#     full_name = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone_number = models.CharField(validators=[phone_regex], max_length=15)
#     subject = models.CharField(max_length=200)
#     message = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Contact from {self.full_name} - {self.subject}"
