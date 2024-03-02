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


# Create your models here.
class Exercise(models.Model):
    DEFAULT_USER = User.objects.get(username="default")
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

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_exercise_list(cls, user):
        exercises = Exercise.objects.filter(Q(user=user) | Q(user=cls.DEFAULT_USER))

        for exercise_name in exercises.values_list("name", flat=True).distinct():
            if Exercise.objects.filter(name=exercise_name, user=user).exists():
                exercises = exercises.exclude(name=exercise_name, user=cls.DEFAULT_USER)

        exercise_names = exercises.values_list("name", flat=True)
        return exercise_names

    @classmethod
    def get_exercise(cls, user, exercise_name):
        exercise = cls.objects.get_or_create(user=user, name=exercise_name)[0]
        return exercise

    def update_five_rep_max(self, weight, reps):
        one_rep_max = weight * (1 + (reps / 30))
        five_rep_max = one_rep_max / (1 + (5 / 30))
        five_rep_max = round(five_rep_max * 4) / 4

        if five_rep_max > self.five_rep_max:
            self.five_rep_max = five_rep_max
            self.save()

            return True


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    exercises = models.ManyToManyField(Exercise, blank=True)
    config = models.JSONField(default=dict)
    DEFAULT_USER = User.objects.get(username="default")

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_workout_list(cls, user):
        # Filter workouts for the current user and default user
        workouts = Workout.objects.filter(Q(user=user) | Q(user=cls.DEFAULT_USER))

        # If a user-specific workout with the same name as a default user's workout exists,
        # exclude the default user's workout from the queryset
        for workout_name in workouts.values_list("name", flat=True).distinct():
            if Workout.objects.filter(name=workout_name, user=user).exists():
                workouts = workouts.exclude(name=workout_name, user=cls.DEFAULT_USER)

        # Retrieve only the names of the workouts
        workout_names = workouts.values_list("name", flat=True)
        return workout_names

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

    def configure_exercise(self, five_rep_max, exercise_sets):
        configured_sets = []
        for exercise_set in exercise_sets:
            match exercise_set["modifier"]:
                case "exact":
                    configured_sets.append(
                        (exercise_set["amount"], exercise_set["reps"])
                    )
                case "percentage":
                    configured_sets.append(
                        (
                            ((exercise_set["amount"] / 100) * five_rep_max),
                            exercise_set["reps"],
                        )
                    )
                case "increment":
                    configured_sets.append(
                        (five_rep_max + exercise_set["amount"], exercise_set["reps"])
                    )
                case "decrement":
                    configured_sets.append(
                        (five_rep_max - exercise_set["amount"], exercise_set["reps"])
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
        with transaction.atomic():
            self.save()
            for exercise in exercises:
                for exercise_name, exercise_sets in exercise.items():
                    exercise = Exercise.get_exercise(self.user, exercise_name)

                    WorkoutSet.save_workout_set(self, exercise, exercise_sets)


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
