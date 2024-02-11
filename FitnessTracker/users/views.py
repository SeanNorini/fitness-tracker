from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .forms import LoginForm, RegistrationForm, SettingsForm
from .utils import (
    create_user,
    send_email_confirmation,
)
from django.contrib.auth.decorators import login_required


# Create your views here.
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

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
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(
                    request,
                    "users/login.html",
                    {
                        "form": LoginForm(),
                        "error": "Invalid username and/or password.",
                    },
                )

    return render(request, "users/login.html", {"form": LoginForm()})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)

    return HttpResponseRedirect(reverse("login"))


def registration(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    # Check for form data
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            # send_email_confirmation(user)
            login(request, user)
            return JsonResponse({"success": True})
        else:
            for error_list in form.errors.values():
                return JsonResponse({"error": error_list})

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
