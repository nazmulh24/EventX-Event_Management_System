from django.db import models


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

    # Many-to-Many : Many participants can join many events
    participants = models.ManyToManyField(
        "Participant",
        related_name="events",
        blank=True,
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


class Participant(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
