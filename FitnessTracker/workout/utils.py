from django.core.exceptions import ObjectDoesNotExist
from .models import *
from users.models import *


def save_workout_session(user, workout_form) -> None:
    workout_log = WorkoutLog()
    workout_name = workout_form.cleaned_data["name"]
    workout = Workout.get_workout(user, workout_name)

    workout_log.workout = workout
    workout_log.user = user
    workout_log.date = workout_form.cleaned_data["date"]
    workout_log.save()

    exercises = workout_form.cleaned_data["exercises"]
    for exercise in exercises["exercises"]:
        ((exercise_name, set_info),) = exercise.items()

        curr_exercise = Exercise.objects.get_or_create(name=exercise_name, user=user)

        for i in range(len(set_info["weight"])):
            set_log = WorkoutSet()
            set_log.workout_log = workout_log
            set_log.exercise = curr_exercise[0]
            set_log.weight = set_info["weight"][i]
            set_log.reps = set_info["reps"][i]
            set_log.save()
    return


def get_exercise(user, exercise_name) -> Exercise:
    DEFAULT_USER = User.objects.get(username="default")
    try:
        exercise = Exercise.objects.get(name=exercise_name, user=user)
    except ObjectDoesNotExist:
        exercise = Exercise.objects.get(name=exercise_name, user=DEFAULT_USER)
    return exercise
