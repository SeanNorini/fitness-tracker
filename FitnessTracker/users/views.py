from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .forms import LoginForm, RegistrationForm, SettingsForm
from .models import User
from .utils import (
    send_email_confirmation,
)
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
            user = form.save()
            # send_email_confirmation(user)
            login(request, user)
            return HttpResponse("success", content_type="text/plain")
        else:
            return render(request, "users/registration_form.html", {"form": form})
    return render(request, "users/registration.html", {"form": RegistrationForm()})


@login_required
def settings(request):
    user = request.user
    if request.method == "POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.gender = form.cleaned_data["gender"]
            user.height = form.cleaned_data["height"]
            user.weight = form.cleaned_data["weight"]
            user.age = form.cleaned_data["age"]
            user.save()
            return JsonResponse({"success": True})
    # user.get_module_list()
    modules = ["workout", "cardio", "log", "stats", "settings"]
    form = SettingsForm()
    for field_name, field in form.fields.items():
        field.widget.attrs["value"] = getattr(user, field_name)
    return render(request, "users/settings.html", {"modules": modules, "form": form})
