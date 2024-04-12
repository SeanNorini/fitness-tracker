from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator,
    MinLengthValidator,
)


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
    def update(cls, user):
        user_settings, _ = cls.objects.get_or_create(user=user)
        most_recent_weight = (
            WeightLog.objects.filter(user=user).order_by("-date").first()
        )

        user_settings.body_weight = most_recent_weight.body_weight
        user_settings.body_fat = most_recent_weight.body_fat
        user_settings.save()

    @classmethod
    def get_unit_of_measurement(cls, user):
        unit_of_measurement = (
            cls.objects.filter(user=user)
            .values_list("unit_of_measurement", flat=True)
            .first()
        )
        return unit_of_measurement

    @classmethod
    def get_distance_unit(cls, user):
        system_of_measurement = (
            cls.objects.filter(user=user).first().system_of_measurement
        )

        if system_of_measurement == "Imperial":
            return "mi"
        else:
            return "km"


class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body_weight = models.FloatField(
        validators=[MinValueValidator(30.0), MaxValueValidator(1000.0)],
    )
    body_fat = models.FloatField(
        validators=[MinValueValidator(5.0), MaxValueValidator(60.0)],
    )
    date = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        UserSettings.update(self.user)

    class Meta:
        # Ensure only one weight entry per user per date
        unique_together = ("user", "date")
