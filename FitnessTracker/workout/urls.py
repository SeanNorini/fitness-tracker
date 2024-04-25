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
        "workout/settings",
        views.WorkoutSettingsView.as_view(),
        name="workout_settings",
    ),
    path(
        "workout/settings/save/",
        views.WorkoutSettingsSaveView.as_view(),
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
