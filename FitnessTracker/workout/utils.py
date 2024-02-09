from .models import *
from users.models import *


def delete_record(obj: object) -> None:
    obj.delete()


def save_session(user, workout_form) -> None:
    workout_log = WorkoutLog()
    workout_name = workout_form.cleaned_data["name"]
    print(workout_name)
    workout = Workout.objects.filter(name=workout_name, user=user)

    if len(workout) == 0:
        default = User.objects.get(username="default")
        workout = Workout.objects.filter(name=workout_name, user=default)

    workout_log.workout = workout[0]
    workout_log.user = user
    workout_log.save()

    exercises = workout_form.cleaned_data["exercises"].split(",")
    weights = workout_form.cleaned_data["weights"].split(",")
    reps = workout_form.cleaned_data["reps"].split(",")

    for i, exercise in enumerate(exercises):
        curr_exercise = Exercise.objects.filter(name=exercise, user=user)

        if len(curr_exercise) == 0:
            default = User.objects.get(username="default")
            curr_exercise = Exercise.objects.filter(name=exercise, user=default)

        if weights[i] == "" or reps[i] == "":
            continue

        curr_set = Set(
            exercise=curr_exercise[0],
            workout_log=workout_log,
            weight=weights[i],
            reps=reps[i],
        )

        curr_set.save()

    return
