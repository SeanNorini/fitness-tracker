from django.urls import re_path, path
from . import views


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
    path("save_weight_log/", views.SaveWeightLogView.as_view(), name="save_weight_log"),
    path(
        "delete_weight_log/<int:pk>",
        views.DeleteWeightLogView.as_view(),
        name="delete_weight_log",
    ),
    path(
        "get_workout_log/<int:pk>",
        views.GetWorkoutLogView.as_view(),
        name="get_workout_log",
    ),
    path(
        "edit_workout_log/<int:pk>/",
        views.EditWorkoutLogView.as_view(),
        name="edit_workout_log",
    ),
    path(
        "update_workout_log/<int:pk>/",
        views.UpdateWorkoutLogView.as_view(),
        name="update_workout_log",
    ),
]
