from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100,default=None, blank=True, null=True)
    last_name = models.CharField(max_length=100,default=None, blank=True, null=True)
    email = models.EmailField(default=None, blank=True, null=True)

    def __str__(self):
        return self.user.username


