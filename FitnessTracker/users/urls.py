from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("activate/<uidb64>/<token>/", views.ActivateView.as_view(), name="activate"),
    path(
        "change_password_form/",
        views.ChangePasswordFormView.as_view(),
        name="change_password_form",
    ),
    path(
        "change_password/",
        views.ChangePasswordAPIView.as_view(),
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
    path("settings/", views.SettingsView.as_view(), name="user_settings"),
    path("delete_account/", views.DeleteUserAPIView.as_view(), name="delete_account"),
    path(
        "settings/update_account_settings/",
        views.UpdateAccountSettingsAPIView.as_view(),
        name="update_account_settings",
    ),
    path(
        "settings/update_user_settings/",
        views.UpdateUserSettingsView.as_view(),
        name="update_user_settings",
    ),
]
