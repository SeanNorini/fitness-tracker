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

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_exercise_list(cls, user):
        return get_attribute_list(Exercise, user, "name")

    @classmethod
    def get_exercise(cls, user, exercise_name):
        exercise, created = cls.objects.get_or_create(user=user, name=exercise_name)
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
            workout = cls.objects.get(name=workout_name, user=user)
        except ObjectDoesNotExist:
            workout = cls.objects.get(name=workout_name, user=default_user)
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
    date = models.DateField()
    time = models.TimeField()
    duration_hours = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(24)]
    )
    duration_minutes = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(59)]
    )
    duration_seconds = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(59)]
    )
    distance = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(99.99)],
    )
