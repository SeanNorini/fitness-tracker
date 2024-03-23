import json
from datetime import date

from dateutil.relativedelta import relativedelta
from matplotlib.ticker import MaxNLocator
from django.db.models import Max
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from users.models import User, UserBodyCompositionSetting, WeightLog, WorkoutSetting
from .forms import (
    WorkoutLogForm,
    ExerciseForm,
)
from users.forms import WorkoutSettingForm
from .utils import *
from matplotlib import pyplot as plt
from io import BytesIO
import matplotlib

matplotlib.use("Agg")


def plot_graph(stat_name, values, dates):
    plt.close()
    plt.plot(dates, values)
    plt.xlabel("Date", color="#f5f5f5")
    plt.ylabel("Lbs.", color="#f5f5f5")
    plt.title(stat_name.capitalize(), color="#f5f5f5")

    plt.gcf().set_facecolor("#212121")
    plt.xticks(color="#f5f5f5")
    plt.yticks(color="#f5f5f5")

    ax = plt.gca()
    ax.set_facecolor("#212121")
    ax.xaxis.set_major_locator(MaxNLocator(12))
    ax.yaxis.set_major_locator(MaxNLocator(15))
    ax.tick_params(color="#f5f5f5")

    for spine in ax.spines.values():
        spine.set_edgecolor("#f5f5f5")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    return buffer.getvalue()


# Create your views here.


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "base/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        DEFAULT_USER = User.objects.get(username="default")
        exercises = list(Exercise.objects.filter(user=DEFAULT_USER))
        context["exercises"] = exercises
        modules = ["workout", "cardio", "log", "stats", "settings"]
        context["modules"] = modules
        context["template_content"] = "workout/stats.html"
        return context

    def post(self, request, *args, **kwargs):
        months = int(request.POST["date_range"])
        stat = request.POST["stat"]
        user = request.user

        start_date = date.today() - relativedelta(months=months)
        end_date = date.today()

        dates = []
        weights = []
        if stat == "weightlifting":
            exercise_name = request.POST["exercise"]
            exercise = Exercise.objects.get(name=exercise_name, user=user)
            max_weight_info = (
                WorkoutSet.objects.filter(
                    exercise=exercise,
                    workout_log__date__range=[start_date, end_date],
                )
                .values("workout_log__date")
                .annotate(max_weight=Max("weight"))
                .order_by("workout_log__date")
            )

            for entry in max_weight_info:
                dates.append(entry["workout_log__date"].strftime("%#m/%#d"))
                weights.append(entry["max_weight"])
            # exercise_values = list(workout_sets.values_list("weight", flat=True))
            graph = plot_graph(exercise_name, weights, dates)
            return HttpResponse(graph, content_type="image/png")
        else:
            weight_info = WeightLog.objects.filter(
                user=user, date__range=[start_date, end_date]
            ).values("date", "body_weight")
            for entry in weight_info:
                dates.append(entry["date"].strftime("%#d/%#m"))
                weights.append(entry["body_weight"])
            graph = plot_graph("Body Weight", weights, dates)
            return HttpResponse(graph, content_type="image/png")

    def get(self, request, *args, **kwargs):
        if request.headers.get("fetch") == "True":
            return render(
                request, "workout/stats.html", self.get_context_data(**kwargs)
            )
        return super().get(self, request, *args, **kwargs)


class SelectWorkoutView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        workout = Workout.get_workout(self.request.user, self.kwargs["workout_name"])
        context["workout"] = workout.configure_workout

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )
        return context


class WorkoutView(LoginRequiredMixin, TemplateView):
    template_name = "base/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["exercises"] = Exercise.get_exercise_list(self.request.user)
        context["workouts"] = Workout.get_workout_list(self.request.user)

        modules = ["workout", "cardio", "log", "stats", "settings"]
        context["modules"] = modules

        context["template_content"] = "workout/workout_session.html"

        user_workout_settings = WorkoutSetting.objects.filter(
            user=self.request.user
        ).first()
        context["show_workout_timer"] = user_workout_settings.show_workout_timer
        context["show_rest_timer"] = user_workout_settings.show_rest_timer

        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("fetch") == "True":
            return render(
                request,
                "workout/workout_session.html",
                self.get_context_data(**kwargs),
            )
        else:
            return render(request, "base/index.html", self.get_context_data(**kwargs))


class AddExerciseView(LoginRequiredMixin, TemplateView):

    template_name = "workout/exercise.html"

    def get_context_data(self, **kwargs):
        exercise = Exercise.get_exercise(self.request.user, self.kwargs["exercise"])

        context = super().get_context_data(**kwargs)
        context["exercise"] = exercise
        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )
        return context


class AddSetView(LoginRequiredMixin, TemplateView):
    template_name = "workout/set.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        exercise_name = self.kwargs.get("exercise_name")
        exercise = Exercise.get_exercise(self.request.user, exercise_name)

        context["set"] = exercise.sets()[0]
        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )

        return context


class SaveWorkoutSessionView(LoginRequiredMixin, FormView):
    form_class = WorkoutLogForm

    def form_valid(self, form, *args, **kwargs):
        workout_log = form.save(commit=False)
        workout_log.user = self.request.user
        workout_log.workout = Workout.get_workout(
            self.request.user, form.cleaned_data["workout_name"]
        )

        success = workout_log.save_workout_session(form.cleaned_data["exercises"])

        if success:
            return JsonResponse({"success": True, "pk": workout_log.pk})
        else:
            return JsonResponse({"success": False})

    def form_invalid(self, form):
        return JsonResponse({"error": "Invalid Form"})


class WorkoutSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        DEFAULT_USER = User.objects.get(username="default")
        exercises = Exercise.objects.filter(user=DEFAULT_USER).values_list(
            "name", flat=True
        )
        workouts = Workout.get_workout_list(self.request.user)
        context["workouts"] = workouts
        context["exercises"] = list(exercises)

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )

        user_workout_settings = WorkoutSetting.objects.filter(
            user=self.request.user
        ).first()
        context["form"] = WorkoutSettingForm(instance=user_workout_settings)
        return context


class WorkoutSettingsSelectWorkoutView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout_settings_workout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        workout = Workout.get_workout(self.request.user, self.kwargs["workout_name"])
        context["workout"] = workout.config
        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )
        return context


class WorkoutSettingsAddSetView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout_settings_set.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = Exercise.get_exercise(
            self.request.user, self.kwargs["exercise_name"]
        )
        context["exercise_set"] = {
            "amount": exercise.default_weight,
            "reps": exercise.default_reps,
            "modifier": exercise.default_modifier,
        }

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )
        return context


class WorkoutSettingsAddExerciseView(LoginRequiredMixin, TemplateView):

    template_name = "workout/workout_settings_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = Exercise.get_exercise(
            self.request.user, self.kwargs["exercise_name"]
        )
        context["exercise"] = exercise

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )

        return context


class WorkoutSettingsSaveWorkoutView(LoginRequiredMixin, UpdateView):
    model = Workout

    def post(self, request, *args, **kwargs):
        workout_name = request.POST.get("workout_name").title()
        workout, created = Workout.objects.get_or_create(
            user=self.request.user, name=workout_name
        )

        exercise_list = [
            json.loads(exercise) for exercise in request.POST.getlist("exercises")
        ]

        workout.config = {"exercises": exercise_list}

        for exercise in exercise_list:

            print(Exercise.objects.get(user=self.request.user, name=exercise["name"]))
            exercise, created = Exercise.objects.get_or_create(
                user=self.request.user, name=exercise["name"]
            )
            if created or exercise not in workout.exercises.all():
                workout.exercises.add(exercise)

        workout.save()

        return JsonResponse({"success": True}, safe=False)


class WorkoutSettingsSaveWorkoutSettingsView(LoginRequiredMixin, FormView):
    model = WorkoutSetting
    form_class = WorkoutSettingForm

    def form_valid(self, form):
        workout_settings, created = WorkoutSetting.objects.get_or_create(
            user=self.request.user
        )
        workout_settings.auto_update_five_rep_max = form.cleaned_data[
            "auto_update_five_rep_max"
        ]
        workout_settings.show_rest_timer = form.cleaned_data["show_rest_timer"]
        workout_settings.show_workout_timer = form.cleaned_data["show_workout_timer"]
        workout_settings.save()

        return JsonResponse({"success": True}, safe=False)


class ExerciseSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "workout/exercise_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exercises"] = Exercise.get_exercise_list(self.request.user)
        return context


class EditExerciseView(LoginRequiredMixin, FormView):
    form_class = ExerciseForm
    template_name = "workout/edit_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise_name = self.kwargs.get("exercise_name")
        context["exercise"] = Exercise.get_exercise(self.request.user, exercise_name)

        context["unit_of_measurement"] = (
            UserBodyCompositionSetting.get_unit_of_measurement(self.request.user)
        )
        return context

    def form_valid(self, form):
        exercise = Exercise.get_exercise(
            user=self.request.user, exercise_name=form.cleaned_data["name"].title()
        )

        exercise.default_reps = form.cleaned_data["default_reps"]
        exercise.default_weight = form.cleaned_data["default_weight"]
        exercise.five_rep_max = form.cleaned_data["five_rep_max"]
        exercise.save()
        return JsonResponse({"success": True}, safe=False)


class ExerciseSettingsDeleteExerciseView(LoginRequiredMixin, DeleteView):
    model = Exercise

    def get_object(self, queryset=None):
        exercise_name = self.kwargs.get("exercise_name")
        pk = self.kwargs.get("pk")
        exercise = Exercise.objects.filter(
            user=self.request.user, pk=pk, name=exercise_name
        ).first()
        return exercise

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return JsonResponse({"success": True})
