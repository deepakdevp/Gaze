from django.db import models
from base.models import Profile

class Voice(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='voices')
    voice_id = models.CharField(max_length=100)
    voice_id_name = models.CharField(max_length=100)
    file_url = models.URLField()

    def __str__(self):
        return f"{self.voice_id_name} - {self.profile.user.username}"