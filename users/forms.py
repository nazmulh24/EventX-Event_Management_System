from django import forms
from django.contrib.auth.models import User
import re
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from events.forms import StyleFormMixin


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


#
class LoginForm(StyleFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
