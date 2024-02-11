from .models import *
from users.models import *
from django.core.exceptions import ObjectDoesNotExist


def save_session(user, workout_form) -> None:
    workout_log = WorkoutLog()
    workout_name = workout_form.cleaned_data["name"]
    workout = get_workout(user, workout_name)

    workout_log.workout = workout
    workout_log.user = user
    workout_log.date = workout_form.cleaned_data["date"]
    workout_log.save()

    exercises = workout_form.cleaned_data["exercises"]
    for exercise in exercises["exercises"]:
        ((exercise_name, set_info),) = exercise.items()

        curr_exercise = get_exercise(user, exercise_name)

        for i in range(len(set_info["weight"])):
            set_log = Set()
            set_log.workout_log = workout_log
            set_log.exercise = curr_exercise
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


def get_workouts(user) -> list[Workout]:
    pass


def get_workout(user, workout_name) -> Workout:
    DEFAULT_USER = User.objects.get(username="default")
    try:
        workout = Workout.objects.get(name=workout_name, user=user)
    except ObjectDoesNotExist:
        workout = Workout.objects.get(name=workout_name, user=DEFAULT_USER)
    return workout


def get_exercises(user) -> list[Exercise]:
    pass


def get_exercise(user, exercise_name) -> Exercise:
    DEFAULT_USER = User.objects.get(username="default")
    try:
        exercise = Exercise.objects.get(name=exercise_name, user=user)
    except ObjectDoesNotExist:
        exercise = Exercise.objects.get(name=exercise_name, user=DEFAULT_USER)
    return exercise


def configure_workout(workout: Workout) -> dict:
    workout_config = {"exercises": []}
    for exercise in workout.config["exercises"]:
        for exercise_name, exercise_config in exercise.items():
            workout_config["exercises"].append(
                {
                    "name": exercise_name,
                    "sets": zip(exercise_config["weight"], exercise_config["reps"]),
                }
            )

    return workout_config
