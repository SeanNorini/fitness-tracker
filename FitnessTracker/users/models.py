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


class UserBodyCompositionSetting(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    MEASUREMENT_CHOICES = [
        ("Imperial", "Imperial"),
        ("Metric", "Metric"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit_of_measurement = models.CharField(
        max_length=8, choices=MEASUREMENT_CHOICES, default="Imperial"
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    height = models.FloatField(
        default=70, validators=[MinValueValidator(20.0), MaxValueValidator(270.0)]
    )
    weight = models.FloatField(
        default=160, validators=[MinValueValidator(30.0), MaxValueValidator(1000.0)]
    )
    bodyfat = models.FloatField(
        default=20, validators=[MinValueValidator(5.0), MaxValueValidator(60.0)]
    )
    age = models.PositiveIntegerField(
        default=30, validators=[MinValueValidator(1), MaxValueValidator(120)]
    )

    @classmethod
    def get_unit_of_measurement(cls, user):
        unit_of_measurement = (
            cls.objects.filter(user=user)
            .values_list("unit_of_measurement", flat=True)
            .first()
        )
        return unit_of_measurement


class WorkoutSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auto_update_five_rep_max = models.BooleanField(default=False)
    show_rest_timer = models.BooleanField(default=False)
    show_workout_timer = models.BooleanField(default=False)


class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField(
        validators=[MinValueValidator(30.0), MaxValueValidator(1000.0)],
    )
    bodyfat = models.FloatField(
        validators=[MinValueValidator(5.0), MaxValueValidator(60.0)],
    )
    date = models.DateField()

    class Meta:
        # Ensure only one weight entry per user per date
        unique_together = ("user", "date")
