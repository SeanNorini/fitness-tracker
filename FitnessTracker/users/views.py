from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .forms import LoginForm, RegistrationForm, SettingsForm, ChangePasswordForm
from .models import User
from .utils import send_activation_link, account_token_generator
from django.contrib.auth.decorators import login_required


# Create your views here.
def user_login(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            remember_me = login_form.cleaned_data["remember_me"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                return redirect("index")
            else:
                return render(
                    request,
                    "users/login.html",
                    {
                        "form": LoginForm(),
                        "error": "Invalid username and/or password.",
                    },
                )
        else:
            return render(
                request,
                "users/login.html",
                {
                    "form": LoginForm(),
                    "error": "Error. Please try again.",
                },
            )
    return render(request, "users/login.html", {"form": LoginForm()})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect("login")


def registration(request):
    if request.user.is_authenticated:
        return redirect("index")
    # Check for form data
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activation_link(request, user)

            return render(
                request,
                "users/registration_confirmation.html",
                {"name": user.first_name, "email": user.email},
            )
        else:
            return render(request, "users/registration_form.html", {"form": form})
    return render(request, "users/registration.html", {"form": RegistrationForm()})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(
            request, "users/login.html", {"message": "success", "form": LoginForm()}
        )
    return render(
        request, "users/login.html", {"activate_error": "True", "form": LoginForm()}
    )


@login_required
def change_password(request):
    form = ChangePasswordForm()
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if not user.check_password(form.cleaned_data["current_password"]):
                form.add_error("current_password", "Incorrect password.")
            if (
                form.cleaned_data["new_password"]
                != form.cleaned_data["confirm_password"]
            ):
                form.add_error("new_password", "Passwords don't match.")
            if not form.errors:
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                login(request, user)
                return render(request, "users/change_password_done.html")
    return render(request, "users/change_password.html", {"form": form})


@login_required
def settings(request):
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
    modules = ["workout", "cardio", "log", "stats", "settings"]
    form = SettingsForm()
    for field_name, field in form.fields.items():
        field.widget.attrs["value"] = getattr(user, field_name)
    return render(request, "users/settings.html", {"modules": modules, "form": form})
