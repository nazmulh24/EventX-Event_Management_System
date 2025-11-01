from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cloudinary.models import CloudinaryField


class HostEventRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.username}"


class CustomUser(AbstractUser):
    # Using CloudinaryField for profile images
    profile_img = CloudinaryField(
        "image",
        blank=True,
        folder="profile_images",
        transformation={
            "quality": "auto:good",
            "fetch_format": "auto",
            "width": 400,
            "height": 400,
            "crop": "fill",
            "gravity": "face",
        },
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username
