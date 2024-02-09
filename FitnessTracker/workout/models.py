from django.db import models
from users.models import User
from datetime import date


# Create your models here.
class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    config = models.JSONField()

    def __str__(self) -> str:
        return self.name


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today())


class Set(models.Model):
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveIntegerField()
