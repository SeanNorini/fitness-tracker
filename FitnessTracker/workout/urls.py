from django.urls import path
from . import views

urlpatterns = [
    path("workout/", views.workout, name="workout"),
    path("", views.workout, name="index"),
]
