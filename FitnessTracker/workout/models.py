from typing import Type
from django.db import models, transaction
from django.db.models import Q
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import get_object_or_404


def get_default_user():
    return User.objects.get(username="default")


def validate_date(date):
    if date > timezone.now().date():
        raise ValidationError("Date cannot be in the future.")

    one_year_ago = timezone.now().date() - timezone.timedelta(days=365)
    if date < one_year_ago:
        raise ValidationError("Date cannot be earlier than one year ago.")


def get_attribute_list(model_class, user, attribute_name):
    default_user = get_default_user()
    objects = model_class.objects.filter(Q(user=user) | Q(user=default_user)).distinct()

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
        exercise_name = exercise_name.strip()
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
            user_workout_settings = WorkoutSettings.objects.filter(user=user).first()

            if user_workout_settings.auto_update_five_rep_max:
                update_five_rep_max = exercise.update_five_rep_max(weight, reps)
            if update_five_rep_max:
                workout_log.workout.update_five_rep_max(exercise)


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

        default_user_routines = Routine.objects.filter(user=get_default_user()).exclude(
            name__in=routine_list
        )

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
