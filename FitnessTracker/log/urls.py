from . import views
from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutLogViewSet, WeightLogViewSet, CardioLogViewSet, FoodLogViewSet

router = DefaultRouter()
router.register(r"workout_logs", WorkoutLogViewSet)
router.register(r"weight_logs", WeightLogViewSet)
router.register(r"cardio_logs", CardioLogViewSet)
router.register(r"food_logs", FoodLogViewSet)

urlpatterns = [
    re_path(
        r"^(?:(?P<year>\d{4})/(?P<month>\d{1,2})/)?$",
        views.LogTemplateView.as_view(),
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
]

api_urlpatterns = [
    path("", include(router.urls)),
]
