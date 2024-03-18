from django.urls import path
from . import views

urlpatterns = [
    path("", views.CardioView.as_view(), name="cardio"),
]
