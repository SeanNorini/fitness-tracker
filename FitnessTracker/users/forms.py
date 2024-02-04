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


class SettingsForm(forms.Form):
    first_name = forms.CharField(
        label="Name*",
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "first_name",
                "name": "first_name",
                "maxlength": "100",
                "placeholder": "First",
            }
        ),
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "last_name",
                "name": "last_name",
                "maxlength": "100",
                "placeholder": "Last",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "example@gmail.com"}),
    )

    gender = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[("Male", "Male"), ("Female", "Female")],
        label="Gender*",
        initial="Male",
        required=False,
    )

    height = forms.FloatField(
        label="Height (In.)*",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "70", "class": "numbers"}),
        validators=[MinValueValidator(36.0), MaxValueValidator(100.0)],
    )

    weight = forms.FloatField(
        label="Weight (Lbs.)*",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "180", "class": "numbers"}),
        validators=[MinValueValidator(80.0), MaxValueValidator(1000.0)],
    )

    age = forms.IntegerField(
        label="Age*",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "30", "class": "numbers"}),
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )


class RegistrationForm(SettingsForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "name": "username",
                "maxlength": "100",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"id": "password", "name": "password", "maxlength": "100"}
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "id": "confirm_password",
                "name": "confirm_password",
                "maxlength": "100",
            }
        ),
    )
