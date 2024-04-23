from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from . import views


urlpatterns = [
    path("", views.StatsView.as_view(), name="stats"),
    path(
        "<str:stat>/<str:range>/",
        views.StatsGraphAPIView.as_view(),
        name="stats_graph",
    ),
]
