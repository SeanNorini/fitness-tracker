from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "name": "username",
                "label": "username",
                "maxlength": "100",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "id": "password",
                "name": "password",
                "label": "password",
                "maxlength": "100",
            }
        )
    )
    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"id": "remember_me"})
    )
