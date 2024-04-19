from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from workout.models import Exercise, Workout, WorkoutSettings
from .validators import (
    validate_not_future_date,
    validate_not_more_than_5_years_ago,
    validate_duration_min,
    validate_duration_max,
)
from users.models import User, UserSettings
from datetime import timedelta
from django.utils import timezone
from cardio.utils import format_duration


# Create your models here.


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(
        default=timezone.now,
        validators=[validate_not_future_date, validate_not_more_than_5_years_ago],
    )
    total_time = models.DurationField(
        default=timedelta(minutes=30),
        validators=[validate_duration_min, validate_duration_max],
    )

    def generate_workout_log(self):
        workout_log = {
            "pk": self.pk,
            "workout_name": self.workout.name,
            "total_time": self.total_time,
            "exercises": [],
        }

        workout_sets = WorkoutSet.objects.filter(workout_log=self).order_by("pk")
        exercise_summary = {"name": workout_sets[0].exercise.name, "sets": []}
        for workout_set in workout_sets:
            if exercise_summary["name"] != workout_set.exercise.name:
                workout_log["exercises"].append(exercise_summary)
                exercise_summary = {"name": workout_set.exercise.name, "sets": []}
            weight = str(workout_set.weight).rstrip("0").rstrip(".")
            exercise_summary["sets"].append(
                {"weight": weight, "reps": workout_set.reps}
            )

        workout_log["exercises"].append(exercise_summary)

        return workout_log

    @classmethod
    def get_logs(cls, user, year, month):
        return cls.objects.filter(user=user, date__year=year, date__month=month)


class WorkoutSet(models.Model):
    workout_log = models.ForeignKey(
        WorkoutLog, on_delete=models.CASCADE, related_name="workout_sets"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.FloatField(
        validators=[MaxValueValidator(1500.0), MinValueValidator(0.0)],
    )
    reps = models.PositiveIntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        user_workout_settings = WorkoutSettings.objects.filter(
            user=self.workout_log.user
        ).first()
        if user_workout_settings and user_workout_settings.auto_update_five_rep_max:
            self.exercise.update_five_rep_max(self.weight, self.reps)


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

    def get_duration(self):
        return format_duration(self.duration.total_seconds())

    def get_pace(self):
        if self.distance > 0:
            return format_duration(self.duration.total_seconds() / self.distance)
        else:
            return "N/A"

    @classmethod
    def get_logs(cls, user, year, month):
        return cls.objects.filter(user=user, datetime__year=year, datetime__month=month)


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
        most_recent_log = (
            WeightLog.objects.filter(user=self.user).order_by("-date").first()
        )
        UserSettings.update(
            self.user, most_recent_log.body_weight, most_recent_log.body_fat
        )

    class Meta:
        # Ensure only one weight entry per user per date
        unique_together = ("user", "date")

    @classmethod
    def get_logs(cls, user, year, month):
        return cls.objects.filter(user=user, date__year=year, date__month=month)


class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="food_logs")
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        unique_together = ("user", "date")


class FoodItem(models.Model):
    log_entry = models.ForeignKey(
        FoodLog, on_delete=models.CASCADE, related_name="food_items"
    )
    name = models.CharField(max_length=200)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    carbs = models.DecimalField(max_digits=5, decimal_places=2)
    fat = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
