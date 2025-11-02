from django.shortcuts import render
from events.models import Event
from django.utils.timezone import make_aware, now as django_now
from django.db.models import Q
from datetime import datetime


def home_view(request):
    now = django_now()

    upcoming_events_qs = Event.objects.filter(
        Q(date__gt=now.date()) | Q(date=now.date(), time__gte=now.time())
    ).order_by("date", "time")

    upcoming_events = upcoming_events_qs[:3]

    next_event = None
    days = hours = minutes = seconds = None
    next_event_time = None

    for event in upcoming_events_qs:
        event_datetime = make_aware(datetime.combine(event.date, event.time))

        if event_datetime > now:
            next_event = event
            time_left = event_datetime - now
            total_seconds = int(time_left.total_seconds())

            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            next_event_time = event_datetime.strftime("%Y-%m-%dT%H:%M:%S")
            break

    context = {
        "upcoming_events": upcoming_events,
        "next_event": next_event,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "next_event_time": next_event_time,
    }
    return render(request, "home.html", context)


def about_us(request):
    return render(request, "about_us.html")


def no_permission(request):
    return render(request, "no_permission.html")


def contact_view(request):
    return render(request, "contact.html")


def is_admin(user):
    return user.groups.filter(name="Admin").exists()


def is_organizer(user):
    return user.groups.filter(name="Organizer").exists()


def is_participant(user):
    return user.groups.filter(name="Participant").exists()


def is_admin_or_organizer(user):
    return user.groups.filter(name__in=["Admin", "Organizer"]).exists()
