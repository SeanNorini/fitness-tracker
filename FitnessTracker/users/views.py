from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.views.generic import FormView, View, DeleteView, UpdateView
from django.contrib.auth import login, authenticate, logout
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .forms import (
    LoginForm,
    UserRegistrationForm,
    UserBodyCompositionForm,
    ChangePasswordForm,
    ResetPasswordForm,
    SetPasswordForm,
    UpdateAccountForm,
)
from .models import User, UserBodyCompositionSetting, WeightLog
from .utils import send_activation_link, account_token_generator, send_reset_link


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
    form_class = UserRegistrationForm
    form_class2 = UserBodyCompositionForm
    success_url = "/registration/success/"

    def post(self, request, *args, **kwargs):
        user_form = UserRegistrationForm(request.POST)
        user_settings_form = UserBodyCompositionForm(request.POST)
        print(request.POST["height"])
        if user_form.is_valid() and user_settings_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.is_active = False
                user.save()

                user_settings = user_settings_form.save(commit=False)
                user_settings.user = user
                user_settings.save()

                # Send email activation link
                send_activation_link(self.request, user)
                self.request.user = user
                # Return confirmation template
                return render(self.request, "users/registration_success.html")

        else:
            print(user_form.errors)
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


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = "users/change_password_form.html"
    form_class = ChangePasswordForm
    success_url = "users/change_password_done/"

    def form_valid(self, form):
        user = self.request.user
        if not user.check_password(form.cleaned_data["current_password"]):
            form.add_error("current_password", "Incorrect password.")
        if not form.errors:
            user.set_password(form.cleaned_data["new_password"])
            user.save()
            login(self.request, user)
            return render(self.request, "users/change_password_done.html")
        else:
            return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
            send_reset_link(self.request, user)
        except User.DoesNotExist:
            pass
        return render(self.request, "users/reset_password_request.html")


class ResetPasswordConfirmView(FormView):
    template_name = "users/reset_password_change_password.html"
    form_class = SetPasswordForm
    success_url = "/users/change_password_done/"

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data["new_password"])
        self.request.user.save()
        login(self.request, self.request.user)
        return render(self.request, "users/change_password_done.html")

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


class UserSettingsView(LoginRequiredMixin, FormView):
    form_class = UpdateAccountForm
    form_class2 = UserBodyCompositionForm

    def get(self, request, *args, **kwargs):
        user_account_form = UpdateAccountForm(instance=self.request.user)

        user_settings_instance = UserBodyCompositionSetting.objects.filter(
            user=self.request.user
        ).first()

        user_body_composition_form = UserBodyCompositionForm(
            instance=user_settings_instance
        )

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                request,
                "users/settings.html",
                {
                    "form": user_account_form,
                    "form2": user_body_composition_form,
                },
            )
        else:
            modules = ["workout", "cardio", "log", "stats", "settings"]
            return render(
                request,
                "base/index.html",
                {
                    "modules": modules,
                    "form": user_account_form,
                    "form2": user_body_composition_form,
                    "template_content": "users/settings.html",
                },
            )


class DeleteUserView(LoginRequiredMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return redirect("login")


class UpdateAccountSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UpdateAccountForm
    template_name = "users/account_settings_form.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        message = "Account updated successfully"
        return render(
            self.request, self.template_name, {"form": form, "message": message}
        )

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})


class UpdateBodyCompositionSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserBodyCompositionForm
    template_name = "users/body_composition_form.html"

    def get_object(self, queryset=None):
        return UserBodyCompositionSetting.objects.filter(user=self.request.user).first()

    def form_valid(self, form):
        user_body_composition_settings = form.save(commit=False)
        user_body_composition_settings.user = self.request.user
        user_body_composition_settings.save()

        weight = user_body_composition_settings.weight
        bodyfat = user_body_composition_settings.bodyfat
        WeightLog.objects.update_or_create(
            user=self.request.user,
            date=timezone.localdate(),
            defaults={"weight": weight, "bodyfat": bodyfat},
        )

        message = "Body composition updated successfully"
        return render(
            self.request, self.template_name, {"form2": form, "message": message}
        )

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form2": form})
