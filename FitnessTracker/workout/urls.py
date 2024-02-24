from django.urls import path
from . import views

urlpatterns = [
    path("workout/", views.WorkoutView.as_view(), name="workout"),
    path("", views.WorkoutView.as_view(), name="index"),
    path("cardio/", views.WorkoutView.as_view(), name="cardio"),
    path("stats/", views.StatsView.as_view(), name="stats"),
    path(
        "add_exercise/<str:exercise>",
        views.AddExerciseView.as_view(),
        name="add_exercise",
    ),
    path(
        "select_workout/<str:workout_name>",
        views.SelectWorkoutView.as_view(),
        name="select_workout",
    ),
    path(
        "save_workout_session",
        views.SaveWorkoutSessionView.as_view(),
        name="save_workout_session",
    ),
    path("save_workout", views.SaveWorkoutView.as_view(), name="save_workout"),
    path("add_set", views.AddSetView.as_view(), name="add_set"),
    path("edit_workouts", views.edit_workouts, name="edit_workouts"),
    path("exit_edit", views.exit_edit, name="exit_edit"),
]
