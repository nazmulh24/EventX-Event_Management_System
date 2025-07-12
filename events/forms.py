from django import forms
from events.models import Event, Category
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput

from django.contrib.auth import get_user_model

User = get_user_model()


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    default_classes = "w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-green-400 bg-gray-50"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            placeholder = f"Enter {field.label.lower()}" if field.label else ""

            if isinstance(widget, forms.TextInput):
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                        "placeholder": placeholder,
                    }
                )
            elif isinstance(widget, forms.EmailInput):
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                        "placeholder": "your@email.com",
                    }
                )
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                        "placeholder": placeholder,
                        "rows": 3,
                    }
                )
            elif isinstance(widget, forms.Select):
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                    }
                )
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                    }
                )
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update(
                    {
                        "class": f"{self.default_classes} space-y-2",
                    }
                )
            elif isinstance(widget, forms.DateInput):
                widget.attrs.update(
                    {
                        "type": "date",
                        "class": self.default_classes,
                    }
                )
            elif isinstance(widget, forms.TimeInput):
                widget.attrs.update(
                    {
                        "type": "time",
                        "class": self.default_classes,
                    }
                )
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                    }
                )
            else:
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                    }
                )


class EventForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "asset",
            "name",
            "description",
            "date",
            "time",
            "location",
            "category",
        ]

        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }


class ParticipantForm(StyleFormMixin, forms.ModelForm):
    events = forms.ModelMultipleChoiceField(
        queryset=Event.objects.all(), required=False, widget=forms.SelectMultiple
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "events"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()
        if self.instance.pk:
            self.fields["events"].initial = self.instance.joined_events.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def save_m2m(self):
        self.instance.joined_events.set(self.cleaned_data["events"])


class JoinEventForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        return self.cleaned_data["email"]  # allow existing user email


class CategoryForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class AddParticipantForm(StyleFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), label="Confirm Password"
    )

    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Role",
        empty_label="Select Role",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "group",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match")


class EditParticipantForm(StyleFormMixin, forms.ModelForm):
    events = forms.ModelMultipleChoiceField(
        queryset=Event.objects.all(),
        widget=forms.SelectMultiple(),
        required=False,
        label="Associated Events",
    )
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Role",
        empty_label="Select Role",
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-400",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "events",
        ]
