from . import views
from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutLogViewSet, WeightLogViewSet, CardioLogViewSet, FoodLogViewSet

router = DefaultRouter()
router.register(r"workout_log", WorkoutLogViewSet)
router.register(r"weight_log", WeightLogViewSet)
router.register(r"cardio_log", CardioLogViewSet)
router.register(r"food_log", FoodLogViewSet)

urlpatterns = [
    re_path(
        r"^(?:(?P<year>\d{4})/(?P<month>\d{1,2})/)?$",
        views.LogView.as_view(),
        name="log",
    ),
    re_path(
        r"^(?:(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2}))?$",
        views.DailyLogView.as_view(),
        name="daily_log",
    ),
    path(
        "weight_log_template/",
        views.WeightLogTemplateView.as_view(),
        name="weight_log_template",
    ),
    path(
        "workout_log_template/<int:pk>",
        views.WorkoutLogTemplateView.as_view(),
        name="workout_log_template",
    ),
    path(
        "update_workout_log_template/<int:pk>/",
        views.UpdateWorkoutLogTemplateView.as_view(),
        name="update_workout_log_template",
    ),
    path("", include(router.urls)),
]
