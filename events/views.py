from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from events.forms import EventForm, CategoryForm, ParticipantForm, JoinEventForm
from events.models import Event, Category, Participant

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


def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            context = {"form": form, "message": "Event Created Successfully !!!"}
            return render(request, "create_event_form.html", context)
    else:
        form = EventForm()

    context = {"form": form}
    return render(request, "create_event_form.html", context)


def join_event(request, id):
    event = get_object_or_404(Event, pk=id)
    message = None

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")

        if name and email:
            try:
                participant = Participant.objects.get(email=email)
                if participant not in event.participants.all():
                    event.participants.add(participant)
                    message = "You have successfully joined the event!"
                else:
                    message = "You already joined this event."
            except Participant.DoesNotExist:
                participant = Participant.objects.create(name=name, email=email)
                event.participants.add(participant)
                message = "You have been registered and joined the event!"

        else:
            message = "Please provide both name and email."

    return render(
        request,
        "join_event_form.html",
        {
            "event": event,
            "message": message,
        },
    )


def dashboard_view(request):
    type = request.GET.get("type", "today_event")

    participants = Participant.objects.count()
    events = Event.objects.all()

    now = timezone.now()
    today = now.date()
    current_time = now.time()

    counts = Event.objects.aggregate(
        total_event=Count("id"),
        today_event=Count("id", filter=Q(date=today)),
        upcoming_event=Count(
            "id", filter=Q(date__gt=today) | Q(date=today, time__gt=current_time)
        ),
        past_event=Count(
            "id", filter=Q(date__lt=today) | Q(date=today, time__lt=current_time)
        ),
    )

    if type == "total_event":
        events = Event.objects.all()
        title = "Total Events"
    elif type == "upcoming_event":
        events = Event.objects.filter(
            Q(date__gt=today) | Q(date=today, time__gt=current_time)
        )
        title = "Upcoming Events"
    elif type == "past_event":
        events = Event.objects.filter(
            Q(date__lt=today) | Q(date=today, time__lt=current_time)
        )
        title = "Past Events"
    elif type == "today_event":
        events = Event.objects.filter(date=today)
        title = "Today Events"
    else:
        title = "Today Events"
        events = Event.objects.filter(date=today)

    context = {
        "participants": participants,
        "counts": counts,
        "events": events,
        "title": title,
    }
    return render(request, "dashboard.html", context)


def view_detail_dash(request, id):
    events = get_object_or_404(Event, id=id)
    total_participant = events.participants.count()

    return render(
        request,
        "event_details_dash.html",
        {
            "events": events,
            "total_participant": total_participant,
        },
    )


def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        event.name = request.POST.get("name")
        event.description = request.POST.get("description")
        event.date = request.POST.get("date")
        event.time = request.POST.get("time")
        event.location = request.POST.get("location")

        category_id = request.POST.get("category")
        if category_id:
            event.category = get_object_or_404(Category, id=category_id)

        event.save()
        return redirect("event")

    return render(
        request,
        "edit_event.html",
        {
            "event": event,
            "categories": categories,
        },
    )


def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == "POST":
        event.delete()

    return redirect("dashboard")


def view_event(request):
    type = request.GET.get("type", "upcoming_event")
    category_id = request.GET.get("category")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    query = request.GET.get("q", "")

    now = timezone.now()
    today = now.date()
    current_time = now.time()

    events = Event.objects.all()
    categorys = Category.objects.all()

    if type == "today_event":
        events = events.filter(date=today, time__gte=current_time)
    else:
        events = events.filter(Q(date__gt=today) | Q(date=today, time__gt=current_time))

    if query:
        events = events.filter(name__icontains=query)

    if start_date and end_date:
        try:
            start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
            events = events.filter(date__range=(start_date_parsed, end_date_parsed))
        except ValueError:
            pass

    if category_id:
        events = events.filter(category_id=category_id)

    counts = Event.objects.aggregate(
        today_event=Count("id", filter=Q(date=today, time__gte=current_time)),
        upcoming_event=Count(
            "id", filter=Q(date__gt=today) | Q(date=today, time__gt=current_time)
        ),
    )

    context = {
        "counts": counts,
        "categorys": categorys,
        "events": events,
        "active_category": int(category_id) if category_id else None,
        "query": query,
    }
    return render(request, "events.html", context)


def view_detail(request, id):
    event = get_object_or_404(Event, id=id)
    return render(
        request,
        "events_details.html",
        {"event": event},
    )


def view_category(request):
    query = request.GET.get("q", "")

    categorys = Category.objects.all()

    total_categories = categorys.count()

    if query:
        categorys = Category.objects.filter(name__icontains=query)

    return render(
        request,
        "categories.html",
        {
            "categorys": categorys,
            "total_categories": total_categories,
            "query": query,
        },
    )


def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            context = {"form": form, "message": "Category added successfully !!!"}
            return render(request, "add_category_form.html", context)
    else:
        form = CategoryForm()

    return render(request, "add_category_form.html", {"form": form})


def edit_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.name = request.POST.get("name")
        category.description = request.POST.get("description")
        category.save()
        return redirect("category")

    return render(
        request,
        "edit_category.html",
        {"category": category},
    )


def delete_category(request, id):
    category = get_object_or_404(Category, id=id)

    category.delete()
    return redirect("category")


def view_participant(request):
    query = request.GET.get("q", "")

    # participants = Participant.objects.all()
    participants = Participant.objects.prefetch_related("events").all()

    total_participants = participants.count()

    if query:
        participants = Participant.objects.filter(name__icontains=query)

    return render(
        request,
        "participants.html",
        {
            "participants": participants,
            "total_participants": total_participants,
        },
    )


def add_participant(request):
    events = Event.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        selected_event_ids = request.POST.getlist("events")

        try:
            participant = Participant.objects.create(name=name, email=email)
            participant.events.set(selected_event_ids)
            context = {
                "message": "Participant added successfully !!!",
                "events": events,
            }
        except IntegrityError:
            context = {
                "message": "Same email already exists !",
                "events": events,
            }
        return render(request, "add_participant_form.html", context)

    return render(
        request,
        "add_participant_form.html",
        {"events": events},
    )


def edit_participant(request, id):
    participant = get_object_or_404(Participant, id=id)
    events = Event.objects.all()

    if request.method == "POST":
        participant.name = request.POST.get("name")
        participant.email = request.POST.get("email")
        selected_event_ids = request.POST.getlist("events")
        participant.save()
        participant.events.set(selected_event_ids)
        return redirect("participant")

    return render(
        request,
        "edit_participant.html",
        {
            "participant": participant,
            "events": events,
        },
    )


def delate_participant(request, id):
    participant = get_object_or_404(Participant, id=id)

    participant.delete()
    return redirect("participant")


def about_us(request):
    return render(request, "about_us.html")


#
