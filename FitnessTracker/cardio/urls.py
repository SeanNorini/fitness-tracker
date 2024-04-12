from django.urls import path
from . import views

urlpatterns = [
    path("", views.CardioView.as_view(), name="cardio"),
    path(
        "create_cardio_log/",
        views.CreateCardioLogAPIView.as_view(),
        name="create_cardio_log",
    ),
    path(
        "get_cardio_log_summaries/<str:selected_range>/",
        views.GetCardioLogSummariesAPIView.as_view(),
        name="get_cardio_log_summaries",
    ),
]
