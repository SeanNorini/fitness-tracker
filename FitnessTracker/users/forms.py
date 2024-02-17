from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from .models import User


def get_username_field():
    return forms.CharField(
        min_length=2,
        max_length=254,
        label="Username or Email",
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "name": "username",
                "maxlength": 254,
                "autofocus": True,
            }
        ),
    )


def get_password_field(label_prefix="", id_prefix=""):
    field_id = f"{id_prefix}password"
    field_name = f"{id_prefix}password"
    return forms.CharField(
        label=f"{label_prefix}Password",
        min_length=8,
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "id": field_id,
                "name": field_name,
                "maxlength": 100,
            },
        ),
    )


class ResetPasswordForm(forms.Form):
    username = get_username_field()


class LoginForm(forms.Form):
    username = get_username_field()
    password = get_password_field()
    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"id": "remember_me"})
    )


class SetPasswordForm(forms.Form):
    new_password = get_password_field(label_prefix="New ", id_prefix="new_")
    confirm_password = get_password_field(label_prefix="Confirm ", id_prefix="confirm_")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if new password and confirm password match
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("new_password", "Passwords don't match. Please try again.")

        return cleaned_data


class ChangePasswordForm(SetPasswordForm):
    current_password = get_password_field(label_prefix="Current ", id_prefix="current_")


class SettingsForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Name",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "first_name",
                "name": "first_name",
                "maxlength": 100,
                "placeholder": "First",
            }
        ),
    )
    last_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "id": "last_name",
                "name": "last_name",
                "maxlength": 100,
                "placeholder": "Last",
            },
        ),
    )
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"id": "email", "placeholder": "example@gmail.com"}
        ),
    )

    gender = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"id": "gender"}),
        choices=[("M", "Male"), ("F", "Female")],
        label="Gender",
        initial="M",
        required=False,
    )

    height = forms.FloatField(
        label="Height (In.)",
        required=False,
        widget=forms.NumberInput(
            attrs={"id": "height", "placeholder": 70, "class": "numbers"}
        ),
        validators=[MinValueValidator(20.0), MaxValueValidator(120.0)],
    )

    weight = forms.FloatField(
        label="Weight (Lbs.)",
        required=False,
        widget=forms.NumberInput(
            attrs={"id": "weight", "placeholder": 160, "class": "numbers"}
        ),
        validators=[MinValueValidator(50.0), MaxValueValidator(1000.0)],
    )

    age = forms.IntegerField(
        label="Age",
        required=False,
        widget=forms.NumberInput(
            attrs={"id": "age", "placeholder": 30, "class": "numbers"}
        ),
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "gender",
            "height",
            "weight",
            "age",
        ]


class RegistrationForm(SettingsForm):
    username = forms.CharField(
        min_length=2,
        max_length=254,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "name": "username",
                "maxlength": 100,
                "autofocus": True,
            }
        ),
    )
    password = get_password_field()
    confirm_password = get_password_field(label_prefix="Confirm ", id_prefix="confirm_")

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
        if password:
            validate_password(password)

        if password != confirm_password:
            self.add_error("confirm_password", "Passwords don't match.")

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
