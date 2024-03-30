from django.urls import path
from . import views

urlpatterns = [
    path("", views.CardioView.as_view(), name="cardio"),
    path(
        "save_cardio_session/",
        views.SaveCardioSessionView.as_view(),
        name="save_cardio_session",
    ),
    path("get_cardio_log/", views.GetCardioLogView.as_view(), name="get_cardio_log"),
    path(
        "get_cardio_summaries/<str:selected_range>/",
        views.GetCardioSummariesAPIView.as_view(),
        name="get_cardio_summaries",
    ),
]
