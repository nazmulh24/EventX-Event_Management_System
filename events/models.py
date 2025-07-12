from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)

    # Many-to-One : Many events can belong to one category
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="events",
    )

    participants = models.ManyToManyField(
        # User,
        settings.AUTH_USER_MODEL,
        related_name="events",
        blank=True,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
    )

    asset = models.ImageField(
        upload_to="event_asset",
        blank=True,
        null=True,
        default="event_asset/default_img.jpg",
    )

    def __str__(self):
        return f"{self.name}"

    @property
    def total_participants(self):
        return self.participants.count()

    @property
    def available_seats(self):
        MAX_SEATS = 45
        return MAX_SEATS - self.total_participants
