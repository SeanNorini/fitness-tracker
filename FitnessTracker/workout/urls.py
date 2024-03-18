from django.urls import path
from . import views

urlpatterns = [
    path("workout/", views.WorkoutView.as_view(), name="workout"),
    path("", views.WorkoutView.as_view(), name="index"),
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
    path(
        "workout/add_set/<str:exercise_name>",
        views.AddSetView.as_view(),
        name="add_set",
    ),
    path(
        "workout/workout_settings",
        views.WorkoutSettingsView.as_view(),
        name="workout_settings",
    ),
    path(
        "workout/workout_settings/select_workout/<str:workout_name>",
        views.WorkoutSettingsSelectWorkoutView.as_view(),
        name="workout_settings_select_workout",
    ),
    path(
        "workout/workout_settings/add_exercise/<str:exercise_name>",
        views.WorkoutSettingsAddExerciseView.as_view(),
        name="workout_settings_add_exercise",
    ),
    path(
        "workout/workout_settings/add_set/<str:exercise_name>",
        views.WorkoutSettingsAddSetView.as_view(),
        name="workout_settings_add_set",
    ),
    path(
        "workout/workout_settings/save_workout/",
        views.WorkoutSettingsSaveWorkoutView.as_view(),
        name="workout_settings_save_workout",
    ),
    path(
        "workout/workout_settings/save_workout_settings/",
        views.WorkoutSettingsSaveWorkoutSettingsView.as_view(),
        name="workout_settings_save_workout",
    ),
    path(
        "workout/exercise_settings/",
        views.ExerciseSettingsView.as_view(),
        name="exercise_settings",
    ),
    path(
        "workout/exercise_settings/edit_exercise/<str:exercise_name>",
        views.EditExerciseView.as_view(),
        name="edit_exercise",
    ),
    path(
        "workout/exercise_settings/delete_exercise/<str:exercise_name>/<int:pk>",
        views.ExerciseSettingsDeleteExerciseView.as_view(),
        name="exercise_settings_delete_exercise",
    ),
]
