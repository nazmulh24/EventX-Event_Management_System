from django.shortcuts import render, redirect
from users.forms import CustomSign_UpForm, LoginForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test


def sign_up(request):
    form = CustomSign_UpForm()

    if request.method == "POST":
        form = CustomSign_UpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("pass1"))
            user.is_active = False
            user.save()
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
