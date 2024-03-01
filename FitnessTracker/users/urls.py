from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("activate/<uidb64>/<token>/", views.ActivateView.as_view(), name="activate"),
    path(
        "change_password/",
        views.ChangePasswordView.as_view(),
        name="change_password",
    ),
    path("reset_password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path(
        "reset_password/<uidb64>/<token>/",
        views.ResetPasswordConfirmView.as_view(),
        name="reset_password_confirm_token",
    ),
    path(
        "reset_password_confirm/",
        views.ResetPasswordConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path("settings/", views.UserSettingsView.as_view(), name="user_settings"),
    path("delete_account/", views.DeleteUserView.as_view(), name="delete_account"),
    path(
        "settings/update_account_settings/",
        views.UpdateAccountSettingsView.as_view(),
        name="update_account_settings",
    ),
    path(
        "settings/update_body_composition_settings/",
        views.UpdateBodyCompositionSettingsView.as_view(),
        name="update_body_composition_settings",
    ),
]
