from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .forms import LoginForm


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
        else:
            return render(request, "users/login.html", {"form": LoginForm()})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
                user.remember_me = False
                user.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "users/login.html",
                {"form": LoginForm(), "message": "Invalid username and/or password."},
            )

    return render(request, "users/login.html", {"form": LoginForm()})


def registration(request):
    return render(request, "users/registration.html")
