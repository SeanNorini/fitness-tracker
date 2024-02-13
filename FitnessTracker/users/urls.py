from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("registration/", views.registration, name="registration"),
    path("settings/", views.settings, name="settings"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path(
        "change_password/",
        views.change_password,
        name="change_password",
    ),
]
