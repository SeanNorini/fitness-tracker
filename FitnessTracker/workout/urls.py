from django.urls import path
from . import views

urlpatterns = [
    path("workout/", views.WorkoutView.as_view(), name="workout"),
    path("", views.WorkoutView.as_view(), name="index"),
    path("cardio/", views.WorkoutView.as_view(), name="cardio"),
    path("stats/", views.StatsView.as_view(), name="stats"),
    path(
        "workout/add_exercise/<str:exercise>",
        views.AddExerciseView.as_view(),
        name="add_exercise",
    ),
    path(
        "workout/select_workout/<str:workout_name>",
        views.SelectWorkoutView.as_view(),
        name="select_workout",
    ),
    path(
        "workout/save_workout_session",
        views.SaveWorkoutSessionView.as_view(),
        name="save_workout_session",
    ),
    path("workout/save_workout", views.SaveWorkoutView.as_view(), name="save_workout"),
    path("workout/add_set", views.AddSetView.as_view(), name="add_set"),
    path(
        "workout/workout_settings",
        views.EditWorkoutsView.as_view(),
        name="workout_settings",
    ),
    path("exit_edit", views.exit_edit, name="exit_edit"),
]
