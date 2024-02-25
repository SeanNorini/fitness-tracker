from django.urls import re_path
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
]
