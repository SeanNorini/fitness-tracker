from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from users.models import User
from .forms import (
    WorkoutForm,
    WorkoutSessionForm,
)
from .utils import *


# Create your views here.
def stats(request):
    return render(request, "workouts/stats.html")


@login_required
def workout(request):
    DEFAULT_USER = User.objects.get(username="default")
    exercises = list(
        Exercise.objects.filter(user=DEFAULT_USER).values_list("name", flat=True)
    )
    workouts = list(
        Workout.objects.filter(user=DEFAULT_USER).values_list("name", flat=True)
    )
    # exercises.extend(list(Exercise.objects.exclude(name__in=exercises).values_list("name", flat=True)))
    # workouts.extend(list(Workout.objects.exclude(name__in=workouts).values_list("name", flat=True)))

    # user.get_module_list()
    modules = ["workouts", "cardio", "log", "stats", "settings"]
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request,
            "workouts/workout_session.html",
            {"modules": modules, "exercises": exercises, "workouts": workouts},
        )
    else:
        return render(
            request,
            "workouts/index.html",
            {"modules": modules, "exercises": exercises, "workouts": workouts},
        )
    # "workouts": workouts})


@login_required
def add_exercise(request, exercise, sets=None):
    exercise = {"name": exercise.replace("%20", " ")}
    if sets is None:
        exercise["sets"] = [{"weight": "", "reps": ""}]
    else:
        exercise["sets"] = sets

    return render(request, "workouts/exercise.html", {"exercise": exercise})


@login_required
def add_set(request):
    return render(request, "workouts/set.html")


@login_required
def select_workout(request, workout_name):
    workout = get_workout(request.user, workout_name.replace("%20", " "))
    workout_config = configure_workout(workout)

    return render(request, "workouts/workout.html", {"workout": workout_config})


@login_required
def save_workout_session(request):
    if request.method == "POST":
        workout_form = WorkoutSessionForm(request.POST)

        if workout_form.is_valid():
            save_session(request.user, workout_form)

            return JsonResponse({"success": True})
        return JsonResponse({"error": "Invalid Form"})


@login_required
def save_workout(request):
    if request.method == "POST":
        workout_form = WorkoutForm(request.POST)

        if workout_form.is_valid():
            save_custom_workout(request.user, workout_form)

            return JsonResponse({"success": True})
        return JsonResponse({"error": "Invalid Form"})


@login_required
def edit_workouts(request):
    DEFAULT_USER = User.objects.get(username="default")
    exercises = list(
        Exercise.objects.filter(user=DEFAULT_USER).values_list("name", flat=True)
    )
    workouts = list(
        Workout.objects.filter(user=DEFAULT_USER).values_list("name", flat=True)
    )

    return render(
        request,
        "workouts/edit_workouts.html",
        {"workouts": workouts, "exercises": exercises},
    )


@login_required
def exit_edit(request):
    DEFAULT_USER = User.objects.get(username="default")
    exercises = list(
        Exercise.objects.filter(user=DEFAULT_USER).values_list("name", flat=True)
    )
    workouts = list(
        Workout.objects.filter(user=DEFAULT_USER).values_list("name", flat=True)
    )

    return render(
        request,
        "workouts/workout_session.html",
        {"exercises": exercises, "workouts": workouts},
    )
