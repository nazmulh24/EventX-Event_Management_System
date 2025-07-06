# from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404

# from django.http import HttpResponse
# from events.forms import EventForm, CategoryForm, ParticipantForm, JoinEventForm
from events.models import Event, Category

from django.utils import timezone
from django.db.models import Q, Count
from django.utils.timezone import make_aware
from datetime import datetime


def home_view(request):
    now = timezone.now()

    upcoming_events = Event.objects.filter(
        Q(date__gt=now.date()) | Q(date=now.date(), time__gte=now.time())
    ).order_by("date", "time")[:3]

    next_event = (
        Event.objects.filter(
            Q(date__gt=now.date()) | Q(date=now.date(), time__gte=now.time())
        )
        .order_by("date", "time")
        .first()
    )

    days = hours = minutes = seconds = None

    if next_event:
        event_datetime = make_aware(datetime.combine(next_event.date, next_event.time))
        time_left = event_datetime - now

        total_seconds = int(time_left.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

    context = {
        "upcoming_events": upcoming_events,
        "next_event": next_event,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }

    return render(request, "home.html", context)


def about_us(request):
    return render(request, "about_us.html")


def no_permission(request):
    return render(request, "no_permission.html")


def is_admin(user):
    return user.groups.filter(name="Admin").exists()


def is_organizer(user):
    return user.groups.filter(name="Organizer").exists()


def is_participant(user):
    return user.groups.filter(name="Participant").exists()


def is_admin_or_organizer(user):
    return user.groups.filter(name__in=["Admin", "Organizer"]).exists()
