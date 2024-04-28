from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"exercises", views.ExerciseViewSet)
router.register(r"workouts", views.WorkoutViewSet)
router.register(r"routines", views.RoutineViewSet)
router.register(r"routine_settings", views.RoutineSettingsViewSet)
router.register(r"workout_settings", views.WorkoutSettingsViewSet)

urlpatterns = [
    path("workout/", views.WorkoutView.as_view(), name="workout"),
    path("", views.WorkoutView.as_view(), name="index"),
    path(
        "workout/settings",
        views.WorkoutSettingsView.as_view(),
        name="workout_settings",
    ),
    path(
        "workout/exercise_settings/",
        views.ExerciseSettingsView.as_view(),
        name="exercise_settings",
    ),
    path(
        "workout/routine_settings/",
        views.RoutineSettingsView.as_view(),
        name="routine_settings",
    ),
    path(
        "workout/routine_settings/get_active_workout_search_list/",
        views.GetActiveWorkoutSearchListView.as_view(),
        name="get_active_workout_search_list",
    ),
]

api_urlpatterns = [
    path("", include(router.urls)),
]
