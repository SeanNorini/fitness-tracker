from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_date(date):
    if date > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")

    one_year_ago = timezone.now().date() - timezone.timedelta(days=365)
    if date < one_year_ago:
        raise ValidationError("Date cannot be earlier than one year ago.")


# Create your models here.
class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    config = models.JSONField(default=dict)

    def __str__(self) -> str:
        return self.name


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, validators=[validate_date])


class WorkoutExercise(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE)


class WorkoutSet(models.Model):
    exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE)
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MaxValueValidator(1500), MinValueValidator(0)],
    )
    reps = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
