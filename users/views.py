from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from users.forms import CustomSign_UpForm, LoginForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator

from events.models import Event, Category

from django.utils import timezone
from django.db.models import Q, Count
from django.utils.timezone import make_aware
from datetime import datetime

from core.views import is_admin, is_organizer, is_participant
from users.forms import (
    CustomSign_UpForm,
    LoginForm,
    AssignRoleForm,
    CreateGroupForm,
    HostEventRequestForm,
)
from django.db.models import Prefetch


def sign_up(request):
    form = CustomSign_UpForm()

    if request.method == "POST":
        form = CustomSign_UpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("pass1"))
            user.is_active = False
            user.save()

            participant_group = Group.objects.get(
                name="Participant"
            )  # --> Assign default group
            user.groups.add(participant_group)

            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return redirect("sign-in")

    context = {"form": form}
    return render(request, "Registration/sign_up.html", context)


def sign_in(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")

    context = {
        "form": form,
    }
    return render(request, "Registration/sign_in.html", context)


@login_required
def sign_out(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return redirect("sign-in")
        else:
            return HttpResponse("Invalid ID / Token...")

    except User.DoesNotExist:
        return HttpResponse("User Not Found")


@user_passes_test(is_admin, login_url="no-permission")
def admin_dashboard(request):
    type = request.GET.get("type", "today_event")

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
    return render(request, "admin/admin_dashboard.html", context)


@user_passes_test(is_admin, login_url="no-permission")
def view_role(request):
    users = User.objects.prefetch_related(
        Prefetch("groups", queryset=Group.objects.all(), to_attr="all_groups")
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = "No Group Assigned"

    context = {
        "users": users,
    }
    return render(request, "admin/user_list.html", context)


@user_passes_test(is_admin, login_url="no-permission")
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == "POST":
        form = AssignRoleForm(request.POST)

        if form.is_valid():
            role = form.cleaned_data.get("role")
            user.groups.clear()  # --> Remove old roles
            user.groups.add(role)
            messages.success(request, f"Role '{role}' assigned to {user.username}.")

            return redirect("view-role")

    context = {
        "form": form,
    }
    return render(request, "admin/assign_role.html", context)


@user_passes_test(is_admin, login_url="no-permission")
def create_group(request):
    form = CreateGroupForm()

    if request.method == "POST":
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(
                request, f"Group {group.name} has been created successfully.."
            )
            return redirect("group-list")

    return render(request, "admin/create_group.html", {"form": form})


@user_passes_test(is_admin, login_url="no-permission")
def group_list(request):
    groups = Group.objects.prefetch_related("permissions").all()

    return render(request, "admin/group_list.html", {"groups": groups})


from django.contrib.auth.decorators import login_required
from events.models import Event


@login_required
def organizer_dashboard(request):
    user = request.user
    events = Event.objects.filter(creator=user).order_by("-date")

    return render(
        request,
        "organizer/organizer_dashboard.html",
        {
            "events": events,
        },
    )


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

    return render(request, "host_event_request.html", {"form": form})
