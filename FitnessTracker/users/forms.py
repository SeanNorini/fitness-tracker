from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from .models import User


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


class SettingsForm(forms.ModelForm):
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
        choices=[("M", "Male"), ("F", "Female")],
        label="Gender*",
        initial="M",
        required=False,
    )

    height = forms.FloatField(
        label="Height (In.)*",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "70", "class": "numbers"}),
        validators=[MinValueValidator(20.0), MaxValueValidator(120.0)],
    )

    weight = forms.FloatField(
        label="Weight (Lbs.)*",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "160", "class": "numbers"}),
        validators=[MinValueValidator(50.0), MaxValueValidator(1000.0)],
    )

    age = forms.IntegerField(
        label="Age*",
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "30", "class": "numbers"}),
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
            attrs={
                "id": "password",
                "name": "password",
                "minlength": 8,
                "maxlength": "100",
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "id": "confirm_password",
                "name": "confirm_password",
                "minlength": 8,
                "maxlength": "100",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "email",
            "gender",
            "height",
            "weight",
            "age",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        validate_password(password)

        if password != confirm_password:
            self.add_error("confirm_password", "Passwords don't match")

        # Check if height, weight, and age are not provided
        if not cleaned_data.get("height"):
            cleaned_data["height"] = 70  # Set default height
        if not cleaned_data.get("weight"):
            cleaned_data["weight"] = 160  # Set default weight
        if not cleaned_data.get("age"):
            cleaned_data["age"] = 30  # Set default age

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
