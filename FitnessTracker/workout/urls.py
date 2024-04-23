from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"exercises", views.ExerciseViewSet)
router.register(r"workouts", views.WorkoutViewSet)
router.register(r"routines", views.RoutineViewSet)

urlpatterns = [
    path("workout/", views.WorkoutView.as_view(), name="workout"),
    path("", views.WorkoutView.as_view(), name="index"),
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
        "workout/routine_settings/",
        views.RoutineSettingsView.as_view(),
        name="routine_settings",
    ),
    path(
        "workout/routine_settings/update_routine_settings/",
        views.UpdateRoutineSettingsAPIView.as_view(),
        name="update_routine_settings",
    ),
    path(
        "workout/routine_settings/get_active_workout_search_list/",
        views.GetActiveWorkoutSearchListView.as_view(),
        name="get_active_workout_search_list",
    ),
    path(
        "workout/get_routine_workout/<str:direction>",
        views.GetRoutineWorkoutView.as_view(),
        name="get_routine_workout",
    ),
    path("workout/", include(router.urls)),
]
