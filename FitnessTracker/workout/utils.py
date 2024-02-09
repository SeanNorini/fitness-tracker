from .models import *
from users.models import *
from django.db.models import Q


def save_session(user, workout_form) -> None:
    workout_log = WorkoutLog()
    workout_name = workout_form.cleaned_data["name"]
    workout = Workout.objects.filter(
        Q(name=workout_name, user=user) | Q(name=workout_name, username="default")
    ).first()

    workout_log.workout = workout[0]
    workout_log.user = user
    workout_log.save()

    exercises = workout_form.cleaned_data["exercises"]
    for exercise in exercises["exercises"]:
        ((exercise_name, set_info),) = exercise.items()

        curr_exercise = Exercise.objects.filter(
            Q(name=exercise_name, user=user) | Q(name=exercise_name, user=default)
        ).first()

        for i in range(len(set_info["weight"])):
            set_log = Set()
            set_log.workout_log = workout_log
            set_log.exercise = curr_exercise[0]
            set_log.weight = set_info["weight"][i]
            set_log.reps = set_info["reps"][i]
            set_log.save()
    return


def save_custom_workout(user, workout_form) -> None:
    workout_name = workout_form.cleaned_data["name"]
    config = workout_form.cleaned_data["exercises"]

    Workout.objects.update_or_create(
        name=workout_name,
        user=user,
        defaults={"name": workout_name, "user": user, "config": config},
    )

    return
