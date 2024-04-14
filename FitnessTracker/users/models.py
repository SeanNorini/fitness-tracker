from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator,
    MinLengthValidator,
)
from django.db import models


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(2), RegexValidator(r"^[a-zA-Z]*$")],
        default="first",
    )
    last_name = models.CharField(
        max_length=30,
        validators=[MinLengthValidator(2), RegexValidator(r"^[a-zA-Z]*$")],
        default="last",
    )

    @property
    def distance_unit(self):
        return UserSettings.get_distance_unit(self)

    @property
    def weight_unit(self):
        system_of_measurement = (
            UserSettings.objects.filter(user=self.id).first().system_of_measurement
        )

        if system_of_measurement == "Imperial":
            return "Lbs"
        else:
            return "Kg"

    @property
    def body_weight(self):
        return (
            UserSettings.objects.filter(user=self.id)
            .order_by("-pk")
            .first()
            .body_weight
        )

    @classmethod
    def default_user(cls):
        user, created = User.objects.get_or_create(username="default")
        if created:
            user_settings = UserSettings.objects.create(user=user)
        return user


class UserSettings(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    MEASUREMENT_CHOICES = [
        ("Imperial", "Imperial"),
        ("Metric", "Metric"),
    ]
    user = models.ForeignKey(User, related_name="settings", on_delete=models.CASCADE)
    system_of_measurement = models.CharField(
        max_length=8, choices=MEASUREMENT_CHOICES, default="Imperial"
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    height = models.FloatField(
        default=70, validators=[MinValueValidator(20.0), MaxValueValidator(270.0)]
    )
    body_weight = models.FloatField(
        default=160, validators=[MinValueValidator(30.0), MaxValueValidator(1000.0)]
    )
    body_fat = models.FloatField(
        default=20, validators=[MinValueValidator(5.0), MaxValueValidator(60.0)]
    )
    age = models.PositiveIntegerField(
        default=30, validators=[MinValueValidator(1), MaxValueValidator(120)]
    )

    class Meta:
        verbose_name_plural = "User Settings"

    @classmethod
    def update(cls, user, body_weight, body_fat):
        user_settings, _ = cls.objects.get_or_create(user=user)
        user_settings.body_weight = body_weight
        user_settings.body_fat = body_fat
        user_settings.save()

    @classmethod
    def get_distance_unit(cls, user):
        user_settings, _ = cls.objects.get_or_create(user=user)
        system_of_measurement = user_settings.system_of_measurement

        if system_of_measurement == "Imperial":
            return "mi"
        else:
            return "km"
