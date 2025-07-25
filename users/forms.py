from django import forms
from django.contrib.auth.models import Group, Permission
import re
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from events.forms import StyleFormMixin
from users.models import HostEventRequest, CustomUser

from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSign_UpForm(StyleFormMixin, forms.ModelForm):
    pass1 = forms.CharField(widget=forms.PasswordInput, label="Your Password")
    pass2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "pass1", "pass2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Already Exists.")
        return email

    def clean_pass1(self):
        pass1 = self.cleaned_data.get("pass1")
        errors = []

        if len(pass1) < 8:
            errors.append("Password must be at least 8 characters.")
        if not re.search(r"[!@#$%^&*()\-_=+]", pass1):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise forms.ValidationError(errors)
        return pass1

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("pass1")
        pass2 = cleaned_data.get("pass2")

        if pass1 != pass2:
            raise forms.ValidationError("Password do not match.")
        return cleaned_data


class LoginForm(StyleFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AssignRoleForm(StyleFormMixin, forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(), empty_label="Select Role"
    )


class CreateGroupForm(StyleFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        label="Assign Permissions",
        widget=forms.SelectMultiple(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400",
                "size": 10,
            }
        ),
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]


class HostEventRequestForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = HostEventRequest
        fields = ["motivation"]
        labels = {"motivation": "Why do you want to host events?"}
        widgets = {
            "motivation": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Explain in 2-3 lines",
                }
            )
        }


class StyledPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    pass


class EditProfileForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "bio",
            "profile_img",
        ]


class CustomPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    pass


class CustomPasswordResetForm(StyleFormMixin, PasswordResetForm):
    pass


class CustomConfirmPasswordForm(StyleFormMixin, SetPasswordForm):
    pass
