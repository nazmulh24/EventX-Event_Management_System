from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from users.forms import CustomSign_UpForm, LoginForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from events.models import Event
from django.utils import timezone
from django.db.models import Q, Count
from core.views import is_admin, is_organizer, is_participant
from users.forms import (
    CustomSign_UpForm,
    LoginForm,
    AssignRoleForm,
    CreateGroupForm,
    HostEventRequestForm,
    EditProfileForm,
    CustomPasswordChangeForm,
    CustomConfirmPasswordForm,
    CustomPasswordResetForm,
)
from django.db.models import Prefetch
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.urls import reverse_lazy

from django.views.generic import TemplateView, UpdateView
from django.utils.decorators import method_decorator

from django.contrib.auth import get_user_model

User = get_user_model()


########################################################################################


class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["username"] = user.username
        context["email"] = user.email
        context["name"] = user.get_full_name()
        context["bio"] = user.bio
        context["profile_img"] = user.profile_img

        context["member_since"] = user.date_joined
        context["last_login"] = user.last_login

        return context


class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # user_profile = getattr(
        #     user, "userprofile", None
        # ) 

        context["username"] = user.username
        context["email"] = user.email
        context["name"] = user.get_full_name()
        context["bio"] = user.bio
        context["profile_img"] = user.profile_img

        context["member_since"] = user.date_joined
        context["last_login"] = user.last_login

        return context


class UpdateProfile(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "accounts/update_profile.html"
    context_object_name = "form"

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect("profile")


class ChangePassword(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = CustomPasswordChangeForm


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "Registration/reset_password.html"
    success_url = reverse_lazy("sign-in")
    html_email_template_name = "registration/reset_email.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["protocol"] = "https" if self.request.is_secure() else "http"
        context["domain"] = self.request.get_host()

        return context

    def form_valid(self, form):
        messages.success(self.request, "A reset email send. Please check your email...")
        return super().form_valid(form)


class PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomConfirmPasswordForm
    template_name = "Registration/reset_password.html"
    success_url = reverse_lazy("sign-in")

    def form_valid(self, form):
        messages.success(self.request, "Password has been reset successfully...")
        return super().form_valid(form)


########################################################################################


class SignUp(View):
    template_name = "Registration/sign_up.html"
    form_class = CustomSign_UpForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("pass1"))
            user.is_active = False
            user.save()

            participant_group = Group.objects.get(name="Participant")
            user.groups.add(participant_group)

            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return redirect("sign-in")

        return render(request, self.template_name, {"form": form})


class ActivateUser(View):
    def get(self, request, user_id, token, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect("sign-in")
            else:
                return HttpResponse("Invalid ID or Token.")

        except User.DoesNotExist:
            return HttpResponse("User not found.")


class CustomLogIN(LoginView):
    form_class = LoginForm
    template_name = "Registration/sign_in.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")

        if next_url:
            return next_url

        user = self.request.user
        if user.groups.filter(name="Admin").exists():
            return reverse_lazy("admin-dashboard")
        return reverse_lazy("home")


admin_dashboard_decorators = [
    login_required,
    user_passes_test(is_admin, login_url="/no-permission/"),
]


@method_decorator(admin_dashboard_decorators, name="dispatch")
class AdminDashboard(TemplateView):
    template_name = "admin/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request
        type = request.GET.get("type", "today_event")

        now = timezone.now()
        today = now.date()
        current_time = now.time()

        context["participants"] = User.objects.filter(
            groups__name="Participant"
        ).count()

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
            events = Event.objects.filter(date=today)
            title = "Today Events"

        context.update(
            {
                "counts": counts,
                "events": events,
                "title": title,
            }
        )

        return context


view_role_decorators = [
    login_required,
    user_passes_test(is_admin, login_url="/no-permission/"),
]


@method_decorator(view_role_decorators, name="dispatch")
class ViewRole(TemplateView):
    template_name = "admin/user_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = User.objects.prefetch_related(
            Prefetch("groups", queryset=Group.objects.all(), to_attr="all_groups")
        ).all()

        for user in users:
            user.group_name = (
                user.all_groups[0].name if user.all_groups else "No Group Assigned"
            )

        context["users"] = users
        return context


assign_role_decorators = [
    login_required,
    user_passes_test(is_admin, login_url="/no-permission/"),
]


@method_decorator(assign_role_decorators, name="dispatch")
class AssignRoleView(View):
    template_name = "admin/assign_role.html"
    form_class = AssignRoleForm

    def get(self, request, user_id, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        form = self.form_class(request.POST)

        if form.is_valid():
            role = form.cleaned_data.get("role")
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"Role '{role}' assigned to {user.username}.")
            return redirect("view-role")

        return render(request, self.template_name, {"form": form})


########################################################################################


@login_required
@user_passes_test(is_admin, login_url="/no-permission/")
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


@login_required
@user_passes_test(is_admin, login_url="/no-permission/")
def group_list(request):
    groups = Group.objects.prefetch_related("permissions").all()

    return render(request, "admin/group_list.html", {"groups": groups})


@login_required
@user_passes_test(is_organizer, login_url="/no-permission/")
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
@user_passes_test(is_participant, login_url="/no-permission/")
def host_event_request(request):
    if request.method == "POST":
        form = HostEventRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.save()
            messages.success(request, "Your request has been submitted.")
            return redirect("host-event")
    else:
        form = HostEventRequestForm()

    return render(request, "host_event_request.html", {"form": form})
