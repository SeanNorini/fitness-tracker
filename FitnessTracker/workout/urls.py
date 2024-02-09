from django.urls import path
from . import views

urlpatterns = [
    path("workout/", views.index, name="workout"),
    path("", views.index, name="index"),
    path("", views.index, name="workout"),
    path("", views.index, name="cardio"),
    path("", views.index, name="log"),
    path("", views.index, name="stats"),
    path("add_exercise/<str:exercise>", views.add_exercise, name="add_exercise"),
    path(
        "select_workout/<str:workout_name>", views.select_workout, name="select_workout"
    ),
    path(
        "save_workout_session", views.save_workout_session, name="save_workout_session"
    ),
    path("add_set", views.add_set, name="add_set"),
    path("edit_workouts", views.edit_workouts, name="edit_workouts"),
    path("exit_edit", views.exit_edit, name="exit_edit"),
]
