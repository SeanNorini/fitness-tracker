from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.migrations import serializer
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from calendar import month_name
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from common.permissions import IsOwner
from rest_framework.generics import (
    RetrieveAPIView,
    DestroyAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework import status, viewsets
from .utils import Calendar
from users.models import UserSettings
from workout.models import Workout, Exercise, get_attribute_list
from .serializers import CardioLogSerializer, WorkoutLogSerializer, WeightLogSerializer
from .models import WorkoutLog, CardioLog, WeightLog


# Create your views here.
class LogView(LoginRequiredMixin, TemplateView):
    def get_date(self):
        try:
            year = int(self.kwargs.get("year", ""))
            month = int(self.kwargs.get("month", ""))
            if 1 <= month <= 12:
                return year, month
            else:
                raise ValueError("Month out of range")
        except (ValueError, TypeError):
            return datetime.now().year, datetime.now().month

    def get_workout_logs(self, user, year, month):
        return WorkoutLog.objects.filter(user=user, date__year=year, date__month=month)

    def get_weight_logs(self, user, year, month):
        return WeightLog.objects.filter(user=user, date__year=year, date__month=month)

    def get_cardio_logs(self, user, year, month):
        return CardioLog.objects.filter(
            user=user, datetime__year=year, datetime__month=month
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["year"], context["month"] = self.get_date()

        user = self.request.user
        context["workout_logs"] = self.get_workout_logs(
            user, context["year"], context["month"]
        )
        context["weight_logs"] = self.get_weight_logs(
            user, context["year"], context["month"]
        )
        context["cardio_logs"] = self.get_cardio_logs(
            user, context["year"], context["month"]
        )

        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
        context["modules"] = modules

        calendar = Calendar(
            workout_logs=context["workout_logs"],
            weight_logs=context["weight_logs"],
            cardio_logs=context["cardio_logs"],
        )
        context["calendar"] = calendar.formatmonth(
            year=context["year"], month=context["month"]
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "log/log.html", context)
        context["template_content"] = "log/log.html"
        return render(request, "base/index.html", context)


class DailyLogView(TemplateView):
    template_name = "log/daily_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = context["year"]
        month = context["month"]
        day = context["day"]
        context["month_name"] = month_name[int(month)]

        date = f"{year}-{month}-{day}"

        workout_logs = WorkoutLog.objects.filter(user=self.request.user, date=date)
        context["workout_logs"] = [
            WorkoutLogSerializer(instance=workout_log).data
            for workout_log in workout_logs
        ]

        weight_log = WeightLog.objects.filter(user=self.request.user, date=date).first()
        context["weight_log"] = weight_log

        cardio_logs = CardioLog.objects.filter(
            user=self.request.user, datetime__date=date
        )
        context["cardio_logs"] = cardio_logs

        return context


class WeightLogTemplateView(TemplateView):
    template_name = "log/save_weight_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings = (
            UserSettings.objects.filter(user=self.request.user).order_by("-pk").first()
        )
        context["user_settings"] = user_settings

        return context


class WeightLogViewSet(viewsets.ModelViewSet):
    queryset = WeightLog.objects.all()
    serializer_class = WeightLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class WorkoutLogTemplateView(TemplateView):
    template_name = "log/workout_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs["pk"]
        workout_log = WorkoutLog.objects.get(pk=pk, user=self.request.user)
        context["workout_log"] = WorkoutLogSerializer(instance=workout_log).data
        return context


class UpdateWorkoutLogTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout_session.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        workout_log = WorkoutLog.objects.filter(user=self.request.user, pk=pk).first()
        context["workout"] = WorkoutLogSerializer(instance=workout_log).data

        context["workouts"] = get_attribute_list(Workout, self.request.user, "name")
        context["exercises"] = get_attribute_list(Exercise, self.request.user, "name")
        return context


class WorkoutLogViewSet(viewsets.ModelViewSet):
    queryset = WorkoutLog.objects.all()
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class CardioLogViewSet(viewsets.ModelViewSet):
    queryset = CardioLog.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = CardioLogSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
