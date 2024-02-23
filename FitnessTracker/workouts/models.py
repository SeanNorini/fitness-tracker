from typing import Type

from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist


def validate_date(date):
    if date > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")

    one_year_ago = timezone.now().date() - timezone.timedelta(days=365)
    if date < one_year_ago:
        raise ValidationError("Date cannot be earlier than one year ago.")


# Create your models here.
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    config = models.JSONField(default=dict)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_workout(cls, user, workout_name) -> Type["Workout"]:
        DEFAULT_USER = User.objects.get(username="default")
        try:
            workout = cls.objects.get(name=workout_name, user=user)
        except ObjectDoesNotExist:
            workout = cls.objects.get(name=workout_name, user=DEFAULT_USER)
        return workout

    def configure_workout(self) -> dict:
        workout_config = {"exercises": []}
        for exercise in self.config["exercises"]:
            for exercise_name, exercise_config in exercise.items():
                workout_config["exercises"].append(
                    {
                        "name": exercise_name,
                        "sets": zip(exercise_config["weight"], exercise_config["reps"]),
                    }
                )

        return workout_config


class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, validators=[validate_date])


class WorkoutSet(models.Model):
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MaxValueValidator(1500), MinValueValidator(0)],
    )
    reps = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
