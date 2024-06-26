"""
URL configuration for FitnessTracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from workout.urls import api_urlpatterns as workout_api
from log.urls import api_urlpatterns as log_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("users.urls")),
    path("", include("workout.urls")),
    path("log/", include("log.urls")),
    path("cardio/", include("cardio.urls")),
    path("nutrition/", include("nutrition_tracker.urls")),
    path("stats/", include("stats.urls")),
    path("api/", include(workout_api + log_api)),
]
