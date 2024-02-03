from django.shortcuts import render
from .forms import LoginForm


# Create your views here.
def login(request):
    return render(request, "users/login.html", {"form": LoginForm()})


def registration(request):
    return render(request, "users/registration.html")
