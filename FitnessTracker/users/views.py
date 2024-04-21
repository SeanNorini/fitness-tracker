from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.views.generic import FormView, View
from django.shortcuts import render, redirect, reverse
from django.db.models import Q
from django.db import transaction
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from .forms import (
    LoginForm,
    RegistrationForm,
    UserSettingsForm,
    ChangePasswordForm,
    ResetPasswordForm,
    SetPasswordForm,
    UpdateAccountForm,
)
from workout.models import WorkoutSettings
from .models import User, UserSettings
from .serializers import (
    UpdateAccountSettingsSerializer,
    UpdateUserSettingsSerializer,
)
from .services import (
    change_user_password,
    account_token_generator,
    EmailService,
)


# Create your views here.
class UserLoginView(FormView):
    template_name = "users/login.html"
    form_class = LoginForm
    success_url = "/workout/"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        remember_me = form.cleaned_data["remember_me"]

        # Authenticate user
        user = authenticate(username=username, password=password)
        # Login user if authentication was successful
        if user is not None:
            login(self.request, user)

            # Check remember_me setting
            if not remember_me:
                self.request.session.set_expiry(0)
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid username or password.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("workout")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get("next", self.success_url)


class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect("login")


class RegistrationView(FormView):
    template_name = "users/registration.html"
    form_class = RegistrationForm
    form_class2 = UserSettingsForm
    success_url = "/registration/success/"

    @property
    def email_service(self):
        return EmailService(self.request, self.request.user)

    def post(self, request, *args, **kwargs):
        user_form = RegistrationForm(request.POST)
        user_settings_form = UserSettingsForm(request.POST)

        if user_form.is_valid() and user_settings_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.is_active = False
                user.save()

                user_settings = user_form.save(commit=False)
                user_settings.user = user
                user_settings.save()

                WorkoutSettings.objects.create(user=user)
                self.request.user = user
                # Send email activation link
                self.email_service.send_activation_link()

                # Return confirmation template
                return render(self.request, "users/registration_success.html")

        else:

            return render(
                self.request,
                "users/registration_form.html",
                {"form": user_form, "form2": user_settings_form},
            )

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("workout")
        return render(
            request,
            "users/registration.html",
            {"form": self.form_class, "form2": self.form_class2},
        )


# noinspection PyMethodMayBeStatic
class ActivateView(View):
    template_name = "users/activation_success.html"

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return render(
                request, "users/activation_success.html", {"url": reverse("workout")}
            )
        else:
            return render(
                request, "users/activation_failure.html", {"url": reverse("login")}
            )


class ChangePasswordFormView(LoginRequiredMixin, FormView):
    template_name = "users/change_password_form.html"
    form_class = ChangePasswordForm


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        errors = change_user_password(request.user, **request.data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        update_session_auth_hash(request, request.user)
        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class ResetPasswordView(FormView):
    template_name = "users/reset_password_form.html"
    form_class = ResetPasswordForm
    success_url = "/users/reset_password_request/"

    def form_valid(self, form):
        try:
            username = form.cleaned_data["username"]
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            email_service = EmailService(self.request, user)
            email_service.send_reset_link()
        except User.DoesNotExist:
            pass
        return render(self.request, "users/reset_password_request.html")


class ResetPasswordConfirmView(FormView):
    template_name = "users/reset_password_change_password.html"
    form_class = SetPasswordForm
    success_url = "/users/reset_password_done/"

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data["new_password"])
        self.request.user.save()
        login(self.request, self.request.user)
        return render(self.request, "users/reset_password_done.html")

    def get(self, request, *args, **kwargs):
        uidb64 = self.kwargs.get("uidb64")
        token = self.kwargs.get("token")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_token_generator.check_token(user, token):
            login(self.request, user)
            return render(
                self.request,
                "users/reset_password_change_password.html",
                {"form": SetPasswordForm()},
            )
        else:
            return render(
                self.request,
                "users/reset_password_failure.html",
                {"url": reverse("login")},
            )


class SettingsView(LoginRequiredMixin, FormView):
    form_class = UpdateAccountForm
    form_class2 = UserSettingsForm
    template_name = "base/index.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_settings_instance, _ = UserSettings.objects.get_or_create(
            user=self.request.user
        )

        context["user_settings_form"] = UserSettingsForm(
            instance=user_settings_instance
        )

        context["template_content"] = "users/settings.html"

        return context

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ["users/settings.html"]
        return [self.template_name]


class DeleteUserAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        confirmation = request.data.get("confirmation", "")
        if confirmation != "delete":
            return Response(
                {
                    "error": "Error, confirmation must be entered exactly. Account not deleted."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.delete()
        return Response(
            {"message": "Account successfully deleted."},
            status=status.HTTP_200_OK,
        )


class UpdateAccountSettingsAPIView(UpdateAPIView):
    serializer_class = UpdateAccountSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user


class UpdateUserSettingsAPIView(UpdateAPIView):
    serializer_class = UpdateUserSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return UserSettings.objects.get(user=self.request.user)
