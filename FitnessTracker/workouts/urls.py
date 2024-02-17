from django.urls import path
from . import views

urlpatterns = [
    path("workouts/", views.workout, name="workouts"),
    path("", views.workout, name="index"),
    path("cardio/", views.workout, name="cardio"),
    path("log/", views.workout, name="log"),
    path("stats/", views.stats, name="stats"),
    path("add_exercise/<str:exercise>", views.add_exercise, name="add_exercise"),
    path(
        "select_workout/<str:workout_name>",
        views.select_workout,
        name="select_workout",
    ),
    path(
        "save_workout_session",
        views.save_workout_session,
        name="save_workout_session",
    ),
    path("save_workout", views.save_workout, name="save_workout"),
    path("add_set", views.add_set, name="add_set"),
    path("edit_workouts", views.edit_workouts, name="edit_workouts"),
    path("exit_edit", views.exit_edit, name="exit_edit"),
]
