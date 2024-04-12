from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from .models import User, UserSettings


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


def get_name_field(placeholder=""):
    return forms.CharField(
        label="Name",
        min_length=2,
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": f"{placeholder}_name",
                "name": f"{placeholder}_name",
                "maxlength": 100,
                "placeholder": f"{placeholder.capitalize()}",
            }
        ),
    )


def get_email_field(label_prefix="", id_prefix="", required=True):
    return forms.EmailField(
        label=f"{label_prefix}Email",
        max_length=254,
        required=required,
        widget=forms.EmailInput(
            attrs={"id": f"{id_prefix}email", "placeholder": "example@gmail.com"}
        ),
    )


class RegistrationForm(forms.ModelForm):
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
    email = get_email_field()

    first_name = get_name_field("first")
    last_name = get_name_field("last")

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "email",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password:
            validate_password(password)

        if password != confirm_password:
            self.add_error("confirm_password", "Passwords don't match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


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


class ResetPasswordForm(forms.Form):
    username = get_username_field()


class UserSettingsForm(forms.ModelForm):
    system_of_measurement = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"id": "system_of_measurement"}),
        choices=[("Imperial", "Imperial"), ("Metric", "Metric")],
        label="System of Measurement",
        initial="Imperial",
        required=False,
    )

    gender = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"id": "gender"}),
        choices=[("M", "Male"), ("F", "Female")],
        label="Gender",
        initial="M",
        required=False,
    )

    height = forms.FloatField(
        label="Height (in.)",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "height",
                "placeholder": 70,
                "class": "input input--medium",
                "min": 20,
                "max": 270,
                "step": 0.5,
            }
        ),
        validators=[MinValueValidator(20.0), MaxValueValidator(270.0)],
    )

    body_weight = forms.FloatField(
        label="Body Weight (lbs)",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "body_weight",
                "placeholder": 160,
                "class": "input input--medium",
                "min": 30,
                "max": 1000,
                "step": 0.5,
            }
        ),
        validators=[MinValueValidator(30.0), MaxValueValidator(1000.0)],
    )

    body_fat = forms.FloatField(
        label="Body Fat %",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "body_fat",
                "placeholder": 20,
                "class": "input input--medium",
                "min": 5,
                "max": 60,
                "step": 0.25,
            }
        ),
        validators=[MinValueValidator(5.0), MaxValueValidator(60.0)],
    )

    age = forms.IntegerField(
        label="Age",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "age",
                "placeholder": 30,
                "class": "input input--medium",
                "min": 1,
                "max": 120,
                "step": 1,
            }
        ),
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )

    class Meta:
        model = UserSettings
        fields = [
            "system_of_measurement",
            "gender",
            "height",
            "body_weight",
            "body_fat",
            "age",
        ]

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["system_of_measurement"] = (
            cleaned_data.get("system_of_measurement")
            if cleaned_data.get("system_of_measurement")
            else "Imperial"
        )
        measurement = cleaned_data["system_of_measurement"]

        cleaned_data["gender"] = (
            "M" if not cleaned_data.get("gender") else cleaned_data.get("gender")
        )

        # Check if height, weight, and age are not provided
        if not cleaned_data.get("height"):
            cleaned_data["height"] = (
                70 if measurement == "Imperial" else 175
            )  # Set default height
        if not cleaned_data.get("body_weight"):
            cleaned_data["body_weight"] = (
                160 if measurement == "Imperial" else 70
            )  # Set default weight
        if not cleaned_data.get("age"):
            cleaned_data["age"] = 30  # Set default age
        if not cleaned_data.get("body_fat"):
            cleaned_data["body_fat"] = 20  # Set default age

        return cleaned_data


class UpdateAccountForm(forms.ModelForm):
    first_name = get_name_field("first")
    last_name = get_name_field("last")
    email = get_email_field()
    confirm_email = get_email_field(
        label_prefix="Confirm ", id_prefix="confirm_", required=False
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "confirm_email"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")
        if email != confirm_email and confirm_email != "":
            self.add_error("confirm_email", "Emails don't match.")

        return cleaned_data
