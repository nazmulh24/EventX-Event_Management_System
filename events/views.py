from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from events.forms import (
    EventForm,
    CategoryForm,
    ParticipantForm,
    JoinEventForm,
    AddParticipantForm,
    EditParticipantForm,
)
from users.forms import HostEventRequestForm
from events.models import Event, Category

from django.utils import timezone
from django.db.models import Q, Count
from django.utils.timezone import make_aware
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test, login_required
from core.views import is_admin, is_organizer, is_participant
from django.contrib.auth.models import User
from django.contrib import messages


@user_passes_test(is_organizer, login_url="no-permission")
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            form.save_m2m()

            context = {
                "form": EventForm(),
                "message": "Event Created Successfully!",
            }
            return render(request, "create_event_form.html", context)
    else:
        form = EventForm()

    context = {"form": form}
    return render(request, "create_event_form.html", context)


@login_required
def join_event(request, id):
    event = get_object_or_404(Event, pk=id)
    user = request.user

    if user in event.participants.all():
        messages.warning(request, "You have already joined this event.")
    else:
        event.participants.add(user)
        messages.success(request, "You have successfully joined the event!")

    return redirect("eDetails", event.id)


# @user_passes_test(is_organizer, login_url="no-permission")
def dashboard_view(request):
    type = request.GET.get("type", "today_event")

    # participants = Participant.objects.count()
    participants = User.objects.filter(groups__name="Participant").count()
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
        return redirect("dashboard")

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

    participants = User.objects.prefetch_related("events")

    total_participants = participants.count()

    if query:
        participants = participants.filter(username__icontains=query)

    return render(
        request,
        "participants.html",
        {
            "participants": participants,
            "total_participants": total_participants,
        },
    )


def add_participant(request):
    if request.method == "POST":
        form = AddParticipantForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    password=form.cleaned_data["password"],
                )
                group = form.cleaned_data["group"]
                user.groups.add(group)

                messages.success(request, "Participant created successfully.")
                return redirect("participant")
            except IntegrityError:
                messages.error(request, "Username or email already exists.")
    else:
        form = AddParticipantForm()

    return render(request, "add_participant_form.html", {"form": form})


def edit_participant(request, id):
    participant = get_object_or_404(User, id=id)
    if request.method == "POST":
        form = EditParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            user = form.save()
            user.events.set(form.cleaned_data["events"])
            return redirect("participant")
    else:
        initial = {"events": participant.events.all()}
        form = EditParticipantForm(instance=participant, initial=initial)

    return render(
        request,
        "edit_participant.html",
        {
            "form": form,
            "participant": participant,
        },
    )


def delate_participant(request, id):
    participant = get_object_or_404(User, id=id)

    participant.delete()
    return redirect("participant")


#
@login_required
def event_history(request):
    user = request.user
    now = timezone.now()
    today = timezone.localdate()  # gets current date (no time)

    events = Event.objects.filter(participants=user).order_by("-date", "-time")

    for event in events:
        if event.date < today:
            event.status = "End"
        elif event.date == today:
            event.status = "Ongoing"
        else:
            event.status = "Upcoming"

    return render(request, "event_history.html", {"events": events})


@login_required
def host_event_request(request):
    if request.method == "POST":
        form = HostEventRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.save()
            messages.success(request, "Your request has been submitted.")
            return redirect("dashboard")
    else:
        form = HostEventRequestForm()

    return render(request, "events/host_event_request.html", {"form": form})
