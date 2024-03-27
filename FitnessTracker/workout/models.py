from datetime import timedelta
from typing import Type
from django.db import models, transaction
from django.db.models import Q
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from users.models import WorkoutSetting


def validate_date(date):
    if date > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")

    one_year_ago = timezone.now().date() - timezone.timedelta(days=365)
    if date < one_year_ago:
        raise ValidationError("Date cannot be earlier than one year ago.")


def get_attribute_list(model_class, user, attribute_name):
    objects = model_class.objects.filter(
        Q(user=user) | Q(user=model_class.default_user)
    )

    for value in objects.values_list(attribute_name, flat=True).distinct():
        if model_class.objects.filter(name=value, user=user).exists():
            objects = objects.exclude(name=value, user=model_class.default_user)

    attribute_values = objects.values_list(attribute_name, flat=True)
    return attribute_values


def get_time_from_duration(duration):
    if duration == 0:
        return 0, 0, 0
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)

    return hours, minutes, seconds


def format_duration(duration):
    hours, minutes, seconds = get_time_from_duration(duration)
    if hours > 0:
        return f"{hours}' {minutes:02}' {seconds:02}\""
    else:
        return f"{minutes}' {seconds:02}\""


# Create your models here.
class Exercise(models.Model):
    DEFAULT_MODIFIER_CHOICES = [
        ("add", "Add"),
        ("subtract", "Subtract"),
        ("percentage", "Percentage"),
        ("exact", "Exact"),
    ]

    default_user = User.objects.get(username="default")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    five_rep_max = models.DecimalField(
        default=0,
        max_digits=6,
        decimal_places=2,
        validators=[MaxValueValidator(1500), MinValueValidator(0)],
    )

    default_weight = models.DecimalField(
        default=0,
        max_digits=6,
        decimal_places=2,
        validators=[MaxValueValidator(1500), MinValueValidator(0)],
    )

    default_reps = models.PositiveIntegerField(
        default=8, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )

    default_modifier = models.CharField(
        max_length=20,
        choices=DEFAULT_MODIFIER_CHOICES,
        default="percentage",
    )

    class Meta:
        unique_together = ("user", "name")

    def sets(self):
        return [
            {
                "weight": self.default_weight,
                "reps": self.default_reps,
                "amount": self.default_weight,
                "modifier": self.default_modifier,
            }
        ]

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_exercise_list(cls, user):
        return get_attribute_list(Exercise, user, "name")

    @classmethod
    def get_exercise(cls, user, exercise_name):
        exercise, created = cls.objects.get_or_create(
            user=user, name__iexact=exercise_name
        )
        return exercise

    def update_five_rep_max(self, weight, reps):
        one_rep_max = weight * (1 + (reps / 30))
        five_rep_max = one_rep_max / (1 + (5 / 30))
        five_rep_max = round(five_rep_max * 4) / 4

        if five_rep_max > self.five_rep_max:
            self.five_rep_max = five_rep_max
            self.save()

            return True
        return False


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    exercises = models.ManyToManyField(Exercise, blank=True)
    config = models.JSONField(default=dict)
    default_user = User.objects.get(username="default")

    class Meta:
        unique_together = ("user", "name")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    @classmethod
    def get_workout_list(cls, user):
        return get_attribute_list(Workout, user, "name")

    @classmethod
    def get_workout(cls, user, workout_name) -> Type["Workout"]:
        default_user = User.objects.get(username="default")
        try:
            workout = cls.objects.get(name__iexact=workout_name, user=user)
        except ObjectDoesNotExist:
            workout = cls.objects.get(name__iexact=workout_name, user=default_user)
        return workout

    def configure_workout(self) -> dict:
        workout_config = {"exercises": []}
        for exercise in self.config["exercises"]:
            exercise_sets = self.configure_exercise(
                exercise["five_rep_max"], exercise["sets"]
            )
            workout_config["exercises"].append(
                {
                    "name": exercise["name"],
                    "sets": exercise_sets,
                }
            )

        return workout_config

    @staticmethod
    def configure_exercise(five_rep_max, exercise_sets):
        configured_sets = []
        for exercise_set in exercise_sets:
            match exercise_set["modifier"]:
                case "exact":
                    configured_sets.append(
                        {"weight": exercise_set["amount"], "reps": exercise_set["reps"]}
                    )
                case "percentage":
                    configured_sets.append(
                        {
                            "weight": (exercise_set["amount"] / 100) * five_rep_max,
                            "reps": exercise_set["reps"],
                        }
                    )
                case "increment":
                    configured_sets.append(
                        {
                            "weight": five_rep_max + exercise_set["amount"],
                            "reps": exercise_set["reps"],
                        }
                    )
                case "decrement":
                    configured_sets.append(
                        {
                            "weight": five_rep_max - exercise_set["amount"],
                            "reps": exercise_set["reps"],
                        }
                    )
        return configured_sets

    def update_five_rep_max(self, exercise):
        for workout_exercise in self.config["exercises"]:
            if workout_exercise["name"] == exercise.name:
                workout_exercise["five_rep_max"] = exercise.five_rep_max
                self.save()


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now, validators=[validate_date])
    total_time = models.IntegerField(default=0)

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
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MaxValueValidator(1500), MinValueValidator(0)],
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
            user_workout_settings = WorkoutSetting.objects.filter(user=user).first()

            if user_workout_settings.auto_update_five_rep_max:
                update_five_rep_max = exercise.update_five_rep_max(weight, reps)
            if update_five_rep_max:
                workout_log.workout.update_five_rep_max(exercise)


class CardioLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    duration = models.DurationField(default=timedelta(minutes=30))
    distance = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(99.99)],
    )

    @classmethod
    def get_logs(cls, user, date_range):
        return cls.group_by_day(
            cls.objects.filter(user=user, datetime__date__range=date_range).order_by(
                "datetime"
            )
        )

    @staticmethod
    def group_by_day(logs):

        if len(logs) == 1:
            return [logs]
        elif len(logs) == 0:
            return None

        days = []
        current_day = [logs[0]]

        for i in range(1, len(logs)):
            if logs[i].datetime.date() != current_day[0].datetime.date():
                days.append(current_day)
                current_day = [logs[i]]
            else:
                current_day.append(logs[i])
        days.append(current_day)
        return days

    @staticmethod
    def get_daily_summary(user, logs):
        summary = {
            "date": logs[0].datetime.date(),
            "total_distance": 0,
            "total_duration": 0,
        }

        for log in logs:
            summary["total_distance"] += log.distance
            summary["total_duration"] += log.duration.total_seconds()

        summary["duration"] = format_duration(summary["total_duration"])

        body_weight = user.get_body_weight()
        if user.distance_unit == "mi":
            calories_burned = (summary["total_distance"] * 0.57) * (body_weight * 2.2)
        else:
            calories_burned = (summary["total_distance"] * 1.036) * body_weight
        summary["calories_burned"] = int(calories_burned)

        if summary["total_distance"] > 0:
            summary["pace"] = format_duration(
                summary["total_duration"] // summary["total_distance"]
            )
        else:
            summary["pace"] = "N/A"

        return summary

    @staticmethod
    def get_range_summary(summaries):
        total_distance = 0
        total_duration = 0
        total_summaries = 0
        calories_burned = 0

        for summary in summaries:
            total_distance += summary["total_distance"]
            total_duration += summary["total_duration"]
            calories_burned += summary["calories_burned"]
            total_summaries += 1

        return {
            "total_distance": total_distance,
            "total_duration": total_duration,
            "calories_burned": int(calories_burned / total_summaries),
            "avg_distance": round(total_distance / total_summaries, 2),
            "avg_duration": format_duration(int(total_duration / total_summaries)),
            "pace": format_duration(total_duration // total_distance),
        }

    @classmethod
    def get_summary(cls, user, date_range):
        logs = cls.get_logs(user, date_range)
        if not logs:
            return {
                "avg_distance": 0,
                "avg_duration": "N/A",
                "calories_burned": 0,
                "pace": "N/A",
            }
        summary = cls.get_daily_summary(user, logs[0])
        return summary

    @classmethod
    def get_summary_for_range(cls, user, date_range):
        days = cls.get_logs(user, date_range)
        if days:
            summaries = [cls.get_daily_summary(user, day) for day in days]
        else:
            return {
                "avg_distance": 0,
                "avg_duration": "N/A",
                "calories_burned": 0,
                "pace": "N/A",
            }
        return cls.get_range_summary(summaries)

    @classmethod
    def get_graph_values(cls, user, date_range):
        days = cls.get_logs(user, date_range)
        if days:
            summaries = [cls.get_daily_summary(user, day) for day in days]
            dates = []
            distances = []
            paces = []
            for summary in summaries:
                if summary["total_distance"] == 0:
                    continue

                dates.append(summary["date"].strftime("%m/%d"))
                distances.append(summary["total_distance"])
                paces.append(summary["total_duration"] // summary["total_distance"])
        else:
            return None

        return dates, distances, paces
