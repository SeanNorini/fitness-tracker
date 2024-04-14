from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.core.exceptions import ValidationError
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
def validate_date(date):
    if date > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")

    one_year_ago = timezone.now().date() - timezone.timedelta(days=365 * 5)
    if date < one_year_ago:
        raise ValidationError("Date cannot be earlier than five years ago.")


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, validators=[validate_date])
    total_time = models.DurationField(
        default=timedelta(minutes=30),
        validators=[validate_duration_min, validate_duration_max],
    )

    def save_workout_session(self, exercises):
        try:
            with transaction.atomic():
                self.save()
                for exercise in exercises:
                    for exercise_name, exercise_sets in exercise.items():
                        exercise = Exercise.get_exercise(self.user, exercise_name)

                        WorkoutSet.save_workout_set(self, exercise, exercise_sets)
            return True
        except Exception as e:
            print(e)
            return False

    def update_workout_session(self, exercises):
        self.exercises = None
        workout_sets = WorkoutSet.objects.filter(workout_log=self)
        for workout_set in workout_sets:
            workout_set.delete()

        return self.save_workout_session(exercises)

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


class WorkoutSet(models.Model):
    workout_log = models.ForeignKey(
        WorkoutLog, on_delete=models.CASCADE, related_name="workout_sets"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MaxValueValidator(1500.0), MinValueValidator(0.0)],
    )
    reps = models.PositiveIntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )

    @classmethod
    def save_workout_set(cls, workout_log, exercise, exercise_sets):
        update_five_rep_max = False
        for i in range(len(exercise_sets["weight"])):
            weight = float(exercise_sets["weight"][i])
            reps = int(exercise_sets["reps"][i])

            cls.objects.create(
                workout_log=workout_log,
                exercise=exercise,
                weight=weight,
                reps=reps,
            )

            user = workout_log.user
            user_workout_settings = WorkoutSettings.objects.filter(user=user).first()

            if user_workout_settings.auto_update_five_rep_max:
                update_five_rep_max = exercise.update_five_rep_max(weight, reps)
            if update_five_rep_max:
                workout_log.workout.update_five_rep_max(exercise)


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
