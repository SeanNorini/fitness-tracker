from django.urls import re_path
from . import views


urlpatterns = [
    re_path(
        r"^(?:(?P<year>\d{4})/(?P<month>\d{1,2})/)?$",
        views.LogView.as_view(),
        name="log",
    ),
]
