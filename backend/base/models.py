from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    email = models.EmailField(default=None, blank=True, null=True)
    api_key = models.CharField(max_length=200)
    api_key_mapped = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username



