from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("registration/", views.registration, name="registration"),
    path("settings", views.settings, name="settings"),
    path("user_settings", views.user_settings, name="user_settings"),
]
