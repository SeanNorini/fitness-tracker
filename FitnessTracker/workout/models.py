from typing import Type
from django.db import models, transaction
from django.db.models import Q, When, Case
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


def get_attribute_list(model_class, user, attribute_name):
    default_user = User.default_user()

    objects = model_class.objects.filter(
        Q(user=user) | Q(user=default_user.id)
    ).distinct()

    attribute_values = set()
    user_values = set(objects.filter(user=user).values_list(attribute_name, flat=True))

    # Add user values first
    attribute_values.update(user_values)

    # Add default user values if not already present
    default_user_values = set(
        objects.filter(user=default_user).values_list(attribute_name, flat=True)
    )
    attribute_values.update(default_user_values - user_values)

    return sorted(list(attribute_values))


# Create your models here.
class Exercise(models.Model):
    DEFAULT_MODIFIER_CHOICES = [
        ("add", "Add"),
        ("subtract", "Subtract"),
        ("percentage", "Percentage"),
        ("exact", "Exact"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    five_rep_max = models.FloatField(
        default=0,
        validators=[MaxValueValidator(1500), MinValueValidator(0)],
    )

    default_weight = models.FloatField(
        default=0,
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
        return {
            "weights": [self.default_weight],
            "reps": [self.default_reps],
            "amount": self.default_weight,
            "modifier": self.default_modifier,
        }

    @property
    def set(self):
        return {"weight": self.default_weight, "reps": self.default_reps}

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
        exercise_name = exercise_name.strip().title()
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
        # Get default user
        default_user = User.default_user()

        # Get workout for user or default user, prioritizing user
        workout = (
            cls.objects.filter(
                Q(name__iexact=workout_name), Q(user=user) | Q(user=default_user.id)
            )
            .annotate(
                priority=Case(
                    When(user=user, then=1),
                    When(user=default_user.id, then=2),
                    default=3,
                )
            )
            .order_by("priority")
            .first()
        )

        # If workout does not exist, get custom workout
        if not workout:
            workout, _ = cls.objects.get_or_create(
                user=default_user, name="Custom Workout"
            )

        return workout

    def configure_workout(self) -> dict:
        workout_config = {"exercises": []}

        for exercise in self.config.get("exercises", []):
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


class Routine(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return self.name

    @classmethod
    def get_routines(cls, user):
        user_routines = Routine.objects.filter(user=user)
        routine_list = user_routines.values_list("name", flat=True)

        default_user_routines = Routine.objects.filter(
            user=User.default_user().id
        ).exclude(name__in=routine_list)

        return list(user_routines) + list(default_user_routines)

    def get_weeks(self):
        return Week.objects.filter(routine=self)


class Week(models.Model):
    routine = models.ForeignKey(Routine, related_name="weeks", on_delete=models.CASCADE)
    week_number = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("routine", "week_number")
        ordering = ["week_number"]

    def get_days(self):
        return Day.objects.filter(week=self)

    def __str__(self):
        return f"Week {self.week_number} of {self.routine.name}"


class Day(models.Model):
    week = models.ForeignKey(Week, related_name="days", on_delete=models.CASCADE)
    day_number = models.PositiveSmallIntegerField(
        choices=[(i, f"Day {i}") for i in range(1, 8)]
    )

    class Meta:
        unique_together = ("week", "day_number")
        ordering = ["day_number"]

    def __str__(self):
        return f"{self.get_day_number_display()} of {self.week}"

    def get_workouts(self):
        return Workout.objects.filter(dayworkout__day=self).order_by(
            "dayworkout__order"
        )


class DayWorkout(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # Field to determine the order

    class Meta:
        ordering = ["order"]


Day.add_to_class(
    "workouts",
    models.ManyToManyField(to=Workout, through=DayWorkout, related_name="days"),
)


class RoutineSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    routine = models.ForeignKey(
        Routine, null=True, blank=True, on_delete=models.SET_NULL
    )
    week_number = models.PositiveSmallIntegerField(default=1)
    day_number = models.PositiveSmallIntegerField(default=1)
    workout_index = models.PositiveSmallIntegerField(default=0)
    last_completed = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Routine Settings"

    def _update_workout_day_week(self, direction):
        """Update workout_index, day_number, and week_number based on direction.

        Args:
            direction (str): 'next' for the next workout or 'prev' for the previous workout.
        """
        workouts_count = Workout.objects.filter(dayworkout__day=self._get_day()).count()

        if direction == "next":
            self.workout_index = (self.workout_index + 1) % workouts_count
            if self.workout_index == 0:
                self.day_number = self.day_number % 7 + 1
                if self.day_number == 1:
                    weeks_in_routine = Week.objects.filter(routine=self.routine).count()
                    self.week_number = (self.week_number % weeks_in_routine) + 1
        elif direction == "prev":
            self.workout_index = (self.workout_index - 1) % workouts_count
            if self.workout_index == workouts_count - 1:
                self.day_number = 7 if self.day_number == 1 else self.day_number - 1
                if self.day_number == 7:
                    weeks_in_routine = Week.objects.filter(routine=self.routine).count()
                    self.week_number = (
                        weeks_in_routine
                        if self.week_number == 1
                        else self.week_number - 1
                    )

        self.save()

    def _get_day(self):
        """Retrieve the Day object for the current day_number and week_number."""
        week = get_object_or_404(
            Week, routine=self.routine, week_number=self.week_number
        )
        return get_object_or_404(Day, week=week, day_number=self.day_number)

    def get_workout(self):
        """Retrieve the current workout based on workout_index."""
        day = self._get_day()
        workouts = Workout.objects.filter(dayworkout__day=day).order_by(
            "dayworkout__order"
        )
        try:
            return workouts[self.workout_index]
        except IndexError:
            return None

    def get_next_workout(self):
        """Move to the next workout and retrieve it."""
        self._update_workout_day_week("next")
        return self.get_workout()

    def get_prev_workout(self):
        """Move to the previous workout and retrieve it."""
        self._update_workout_day_week("prev")
        return self.get_workout()


class WorkoutSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auto_update_five_rep_max = models.BooleanField(default=False)
    show_rest_timer = models.BooleanField(default=False)
    show_workout_timer = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Workout Settings"
