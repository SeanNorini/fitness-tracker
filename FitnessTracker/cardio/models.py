from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from .validators import (
    validate_not_future_date,
    validate_not_more_than_5_years_ago,
    validate_duration_min,
    validate_duration_max,
)
from users.models import User
from datetime import timedelta


# Create your models here.
class CardioLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(
        validators=[validate_not_future_date, validate_not_more_than_5_years_ago]
    )
    duration = models.DurationField(
        default=timedelta(minutes=30),
        validators=[validate_duration_min, validate_duration_max],
    )
    distance = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(99.99)],
    )
