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
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]
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
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")
    height = models.FloatField(
        default=70, validators=[MinValueValidator(20.0), MaxValueValidator(120.0)]
    )
    weight = models.FloatField(
        default=160, validators=[MinValueValidator(50.0), MaxValueValidator(1000.0)]
    )
    age = models.PositiveIntegerField(
        default=30, validators=[MinValueValidator(1), MaxValueValidator(120)]
    )


class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField(
        validators=[MinValueValidator(50.0), MaxValueValidator(1000.0)]
    )
    date = models.DateField()

    class Meta:
        # Ensure only one weight entry per user per date
        unique_together = ("user", "date")

    def save(self, *args, **kwargs):
        # Check if there's an existing weight entry for the same date and user
        existing_weight_entry = WeightLog.objects.filter(
            user=self.user, date=self.date
        ).first()
        if existing_weight_entry:
            # Update the existing weight entry with the new weight
            existing_weight_entry.weight = self.weight
            existing_weight_entry.save()
        else:
            # No existing weight entry for the same date and user, create a new one
            super().save(*args, **kwargs)
