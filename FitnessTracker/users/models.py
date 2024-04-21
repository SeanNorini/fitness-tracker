from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
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

    @classmethod
    def get_default_user(cls):
        """
        Retrieve UserSettings from cache or database.
        """
        cache_key = f"default_user"
        default_user = cache.get(cache_key)

        if not default_user:
            default_user, _ = cls.objects.get_or_create(username="default")
            cache.set(cache_key, default_user, timeout=3600)

        return default_user


def default_modules():
    return ["workout", "cardio", "nutrition", "log", "stats", "settings"]


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

    modules = models.JSONField(default=default_modules)

    class Meta:
        verbose_name_plural = "User Settings"

    @classmethod
    def update(cls, user, body_weight, body_fat):
        """
        Updates the user's body weight and body fat settings and refreshes the cache.

        Parameters:
        user (User): The user object whose settings are to be updated.
        body_weight (float): The new body weight to set.
        body_fat (float): The new body fat percentage to set.

        Returns:
        None
        """
        user_settings = cls.get_user_settings(user_id=user.id)
        if (
            user_settings.body_weight != body_weight
            or user_settings.body_fat != body_fat
        ):
            user_settings.body_weight = body_weight
            user_settings.body_fat = body_fat
            user_settings.save()

    @property
    def distance_unit(self):
        system_of_measurement = self.system_of_measurement

        if system_of_measurement == "Imperial":
            return "mi"
        else:
            return "km"

    @property
    def weight_unit(self):
        system_of_measurement = self.system_of_measurement

        if system_of_measurement == "Imperial":
            return "Lbs"
        else:
            return "Kg"

    @staticmethod
    def get_user_settings(user_id):
        """
        Retrieve UserSettings from cache or database.
        """
        cache_key = f"user_settings_{user_id}"
        user_settings = cache.get(cache_key)

        if not user_settings:
            user_settings, _ = UserSettings.objects.get_or_create(user_id=user_id)
            cache.set(cache_key, user_settings, timeout=3600)

        return user_settings

    def save(self, *args, **kwargs):
        """
        Ensure the cache is invalidated or updated when the UserSettings are saved.
        """
        super().save(*args, **kwargs)
        cache_key = f"user_settings_{self.user_id}"
        cache.set(cache_key, self, timeout=3600)

    def delete(self, *args, **kwargs):
        """
        Ensure the cache is invalidated when the UserSettings are deleted.
        """
        super().delete(*args, **kwargs)
        cache_key = f"user_settings_{self.user_id}"
        cache.delete(cache_key)
