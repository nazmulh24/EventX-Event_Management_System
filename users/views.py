from django.shortcuts import render, redirect, HttpResponse
from users.forms import CustomSign_UpForm, LoginForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator


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
        return redirect("sign-in")


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
