from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class HostEventRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.username}"


class CustomUser(AbstractUser):
    profile_img = models.ImageField(
        upload_to="profile_images",
        blank=True,
        default="profile_images/default_pi.png",
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username
