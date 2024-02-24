from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.views.generic import FormView, View
from django.contrib.auth import login, authenticate, logout
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .forms import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    ResetPasswordForm,
    SetPasswordForm,
    SettingsForm,
)
from .models import User
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
            return redirect("workouts")
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
    success_url = "/registration/success/"

    def form_valid(self, form):
        # If form is valid create user
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Send email activation link
        send_activation_link(self.request, user)
        self.request.user = user
        # Return confirmation template
        return render(self.request, "users/registration_success.html")

    def form_invalid(self, form):
        return render(self.request, "users/registration_form.html", {"form": form})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("workouts")
        return super().get(request, *args, **kwargs)


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
                request, "users/activation_success.html", {"url": reverse("workouts")}
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


class SettingsView(LoginRequiredMixin, FormView):
    def get(self, request, *args, **kwargs):
        user = request.user
        # if request.method == "POST":
        #     form = SettingsForm(request.POST)
        #     if form.is_valid():
        #         user.first_name = form.cleaned_data["first_name"]
        #         user.last_name = form.cleaned_data["last_name"]
        #         user.email = form.cleaned_data["email"]
        #         user.gender = form.cleaned_data["gender"]
        #         user.height = form.cleaned_data["height"]
        #         user.weight = form.cleaned_data["weight"]
        #         user.age = form.cleaned_data["age"]
        #         user.save()
        #         return JsonResponse({"success": True})
        # user.get_module_list()
        modules = ["workouts", "cardio", "log", "stats", "settings"]
        form = SettingsForm()
        for field_name, field in form.fields.items():
            field.widget.attrs["value"] = getattr(user, field_name)
        return render(
            request, "users/settings.html", {"modules": modules, "form": form}
        )
