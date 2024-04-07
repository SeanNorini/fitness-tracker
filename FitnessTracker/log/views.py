from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, FormView, DeleteView, UpdateView
from calendar import HTMLCalendar, month_name
from datetime import datetime
from django.shortcuts import get_object_or_404

from users.models import WeightLog, UserBodyCompositionSetting
from workout.models import WorkoutLog, Workout, Exercise, get_attribute_list

from workout.forms import WorkoutLogForm


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

        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
        context["modules"] = modules
        context["css_file"] = "log/css/log.css"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        cal = LogHTMLCalendar(
            workout_logs=context["workout_logs"], weight_logs=context["weight_logs"]
        )
        html_calendar = cal.formatmonth(context["year"], context["month"])
        context["calendar"] = html_calendar

        if request.headers.get("fetch") == "True":

            return render(request, "log/log.html", context)

        context["template_content"] = "log/log.html"
        return render(request, "base/index.html", context)


class LogHTMLCalendar(HTMLCalendar):
    def __init__(self, firstweekday=6, workout_logs=None, weight_logs=None):
        super().__init__(firstweekday)
        self.workout_logs = workout_logs
        self.weight_logs = weight_logs

    def formatday(self, day, weekday):
        workout_log = self.workout_logs.filter(date__day=day).first()
        weight_log = self.weight_logs.filter(date__day=day).first()

        if day == 0:
            day_format = (
                '<td class="noday">&nbsp;</td>'  # If day is 0, display an empty cell
            )
        else:
            day_format = f'<td class="{self.cssclasses[weekday]} day" data-day="{day}"><div>{day}</div>'
            if workout_log is not None:
                day_format += '<div><span class="material-symbols-outlined exercise-icon text-xl">exercise</span></div>'
            if weight_log is not None:
                day_format += (
                    f'<div><span class="material-symbols-outlined monitor_weight-icon text-xl">'
                    f"monitor_weight</span></div>"
                )

            day_format += "</td>"
        return day_format

    def formatmonth(self, year, month, withyear=True):
        # Get the calendar table with the month's days
        cal = super().formatmonth(year, month, withyear)

        # Add a CSS class to the table
        cal = cal.replace(
            '<table border="0" cellpadding="0" cellspacing="0" class="month">',
            '<table class="month">',
        )

        cal = cal.replace(
            f'class="month"',
            f"class='row row-justify-space-between row-align-center full-width month p-0_2'",
        )

        current_month = month_name[month]
        cal = cal.replace(
            f"{current_month} {year}",
            f'<div><span class="material-symbols-outlined hover border bg-tertiary text-xl" id="nav-prev">'
            f"navigate_before</span></div>"
            f'<div id="month-name" data-month={month} data-year={year}>{current_month} {year}</div>'
            f'<div><span class="material-symbols-outlined hover border bg-tertiary text-xl" id="nav-next">'
            f"navigate_next</span></div>",
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

        return context


class EditWorkoutLogView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout_session.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        workout_log = WorkoutLog.objects.filter(user=self.request.user, pk=pk).first()
        context["workout"] = workout_log.generate_workout_log()

        context["workouts"] = get_attribute_list(Workout, self.request.user, "name")
        context["exercises"] = get_attribute_list(Exercise, self.request.user, "name")

        return context


class UpdateWorkoutLogView(LoginRequiredMixin, UpdateView):
    model = WorkoutLog
    form_class = WorkoutLogForm

    def form_valid(self, form):
        workout_log = form.save(commit=False)
        workout_log.user = self.request.user
        workout_log.workout = Workout.get_workout(
            self.request.user, form.cleaned_data["workout_name"]
        )

        success = workout_log.update_workout_session(form.cleaned_data["exercises"])

        if success:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})

    def form_invalid(self, form):
        return JsonResponse({"error": "Invalid Form"})

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter the queryset to objects belonging to the current user
        return queryset.filter(user=self.request.user)


class GetWorkoutLogView(TemplateView):
    template_name = "log/workout_log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs["pk"]
        workout_log = WorkoutLog.objects.get(pk=pk, user=self.request.user)
        context["workout_log"] = workout_log.generate_workout_log()

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

        return context

    def post(self, request, *args, **kwargs):
        body_weight = request.POST.get("body_weight")
        body_fat = request.POST.get("body_fat")
        date = request.POST.get("date")
        date = datetime.strptime(date, "%B %d, %Y")

        weight_log, created = WeightLog.objects.update_or_create(
            user=self.request.user,
            date=date,
            defaults={"body_weight": body_weight, "body_fat": body_fat},
        )

        return JsonResponse({"success": True, "pk": weight_log.pk})


class DeleteWeightLogView(LoginRequiredMixin, DeleteView):
    model = WeightLog

    def form_valid(self, request, *args, **kwargs):
        weight_log = self.get_object()
        success = False
        if weight_log:
            weight_log.delete()
            success = True
        data = {"success": success}
        return JsonResponse(data)


class DeleteWorkoutLogView(LoginRequiredMixin, DeleteView):
    model = WorkoutLog

    def form_valid(self, request, *args, **kwargs):
        workout_log = self.get_object()
        success = False
        if workout_log:
            workout_log.delete()
            success = True
        data = {"success": success}
        return JsonResponse(data)
