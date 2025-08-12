from django import forms
from django.forms import DateInput, TextInput
from pages.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model: Team
        fields = ["first_name", "last_name", "designation", "photo", "facebock_link", "twiter_link", "google_plus_link"]

