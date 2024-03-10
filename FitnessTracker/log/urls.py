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
]
