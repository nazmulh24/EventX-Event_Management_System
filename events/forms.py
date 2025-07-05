from django import forms
from events.models import Event, Category
from django.contrib.auth.models import User


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
            else:
                widget.attrs.update(
                    {
                        "class": self.default_classes,
                    }
                )


class EventForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "category"]
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
