from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Task


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )


class SignUpForm(UserCreationForm):
    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"
        self.fields["password1"].widget.attrs.update({"placeholder": "Create a password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Confirm your password"})

    def clean_username(self):
        email = self.cleaned_data["username"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.username
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "priority", "due_date", "completed"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Plan portfolio update"}),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Add notes, links, or acceptance criteria...",
                }
            ),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
