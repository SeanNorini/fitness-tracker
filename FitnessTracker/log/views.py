from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, FormView
from calendar import HTMLCalendar, month_name
from datetime import datetime

from users.models import WeightLog, UserBodyCompositionSetting
from workout.models import WorkoutLog


# Create your views here.
class LogView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get date from user, return current month on error.
        try:
            context["year"] = int(self.kwargs.get("year"))
            context["month"] = int(self.kwargs.get("month"))
            if context["month"] < 1 or context["month"] > 12:
                raise ValueError("Invalid month")
        except (ValueError, TypeError):
            context["year"] = datetime.now().year
            context["month"] = datetime.now().month

        context["workout_logs"] = WorkoutLog.objects.filter(
            user=self.request.user,
            date__year=context["year"],
            date__month=context["month"],
        )
        context["weight_logs"] = WeightLog.objects.filter(
            user=self.request.user,
            date__year=context["year"],
            date__month=context["month"],
        )

        modules = ["workout", "cardio", "log", "stats", "settings"]
        context["modules"] = modules
        context["css_file"] = "log/css/log.css"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        cal = LogHTMLCalendar(
            workout_logs=context["workout_logs"], weight_logs=context["weight_logs"]
        )
        html_calendar = cal.formatmonth(context["year"], context["month"])
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(request, "log/log.html", {"calendar": html_calendar})

        context["calendar"] = html_calendar
        context["template_content"] = "log/log.html"
        return render(request, "base/index.html", context)


class LogHTMLCalendar(HTMLCalendar):
    def __init__(self, firstweekday=6, workout_logs=None, weight_logs=None):
        super().__init__(firstweekday)
        self.workout_logs = workout_logs
        self.weight_logs = weight_logs

    def formatday(self, day, weekday):
        workout = self.workout_logs.filter(date__day=day).first()
        weight = self.weight_logs.filter(date__day=day).first()

        if day == 0:
            day_format = (
                '<td class="noday">&nbsp;</td>'  # If day is 0, display an empty cell
            )
        else:
            day_format = f'<td class="{self.cssclasses[weekday]} day" data-day="{day}"><div>{day}</div>'
            if workout is not None:
                day_format += '<div><span class="material-symbols-outlined exercise_icon">exercise</span></div>'
            if weight is not None:
                day_format += '<div><span class="material-symbols-outlined weight_icon">monitor_weight</span></div>'
            day_format += "</td>"
        return day_format

    def formatmonth(self, year, month, withyear=True):
        # Get the calendar table with the month's days
        cal = super().formatmonth(year, month, withyear)

        # Add a CSS class to the table
        cal = cal.replace(
            '<table border="0" cellpadding="0" cellspacing="0" class="month">',
            '<table class="calendar month">',
        )

        current_month = month_name[month]
        cal = cal.replace(
            f"{current_month} {year}",
            f'<div><span class="material-symbols-outlined" id="nav_prev">navigate_before</span></div> \
            <div id="month_name" data-month={month} data-year={year}>{current_month} {year}</div> \
            <div><span class="material-symbols-outlined" id="nav_next">navigate_next</span></div>',
        )

        return cal


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
            workout_log.generate_workout_log() for workout_log in workout_logs
        ]

        weight_log = WeightLog.objects.filter(user=self.request.user, date=date).first()
        context["weight_log"] = weight_log

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )

        return context


class SaveWeightLogView(TemplateView):
    template_name = "log/save_weight_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_body_composition_settings = (
            UserBodyCompositionSetting.objects.filter(user=self.request.user)
            .order_by("-pk")
            .first()
        )

        context["user_body_composition_settings"] = user_body_composition_settings

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )
        return context

    def post(self, request, *args, **kwargs):
        weight = request.POST.get("bodyweight")
        bodyfat = request.POST.get("bodyfat")
        date = request.POST.get("date")
        date = datetime.strptime(date, "%B %d, %Y")

        WeightLog.objects.update_or_create(
            user=self.request.user,
            date=date,
            defaults={"weight": weight, "bodyfat": bodyfat},
        )

        return JsonResponse({"success": True})
