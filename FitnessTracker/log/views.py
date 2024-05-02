from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from calendar import month_name
from datetime import datetime
from common.base import BaseOwnerViewSet, BaseTemplateView
from .utils import Calendar
from workout.models import Workout, Exercise
from workout.base import ExerciseTemplateView
from .serializers import (
    CardioLogSerializer,
    WorkoutLogSerializer,
    WeightLogSerializer,
    FoodLogSerializer,
)
from .models import WorkoutLog, CardioLog, WeightLog, FoodLog


# Create your views here.
class LogTemplateView(BaseTemplateView, TemplateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year, month = self.get_date()
        user = self.request.user

        context["calendar"] = Calendar(user=user, year=year, month=month).formatmonth()

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "log/log.html", context)
        context["template_content"] = "log/log.html"
        return render(request, "base/index.html", context)


class DailyLogView(BaseTemplateView, TemplateView):
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


class WeightLogTemplateView(BaseTemplateView, TemplateView):
    template_name = "log/save_weight_log.html"


class WeightLogViewSet(BaseOwnerViewSet):
    queryset = WeightLog.objects.all()
    serializer_class = WeightLogSerializer


class WorkoutLogTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "log/workout_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs["pk"]
        workout_log = WorkoutLog.objects.get(pk=pk, user=self.request.user)
        context["workout_log"] = WorkoutLogSerializer(instance=workout_log).data
        return context


class UpdateWorkoutLogTemplateView(ExerciseTemplateView):
    template_name = "workout/workout_session.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        workout_log = WorkoutLog.objects.filter(user=self.request.user, pk=pk).first()
        context["workout"] = WorkoutLogSerializer(
            instance=workout_log, context={"include_defaults": True}
        ).data

        context["workouts"] = Workout.get_workout_list(self.request.user)

        return context


class WorkoutLogViewSet(BaseOwnerViewSet):
    queryset = WorkoutLog.objects.all()
    serializer_class = WorkoutLogSerializer


class CardioLogViewSet(BaseOwnerViewSet):
    queryset = CardioLog.objects.all()
    serializer_class = CardioLogSerializer


class FoodLogViewSet(BaseOwnerViewSet):
    queryset = FoodLog.objects.all()
    serializer_class = FoodLogSerializer
