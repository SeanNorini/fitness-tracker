from django.urls import path
from . import views

urlpatterns = [
    path("", views.CardioTemplateView.as_view(), name="cardio"),
    path(
        "cardio_log_summaries/<str:selected_range>/",
        views.CardioLogSummariesAPIView.as_view(),
        name="cardio_log_summaries",
    ),
]
