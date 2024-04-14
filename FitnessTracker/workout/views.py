import json
from datetime import date
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    RetrieveAPIView,
    DestroyAPIView,
    CreateAPIView,
    UpdateAPIView,
)

from common.permissions import IsOwner
from log.models import WorkoutSet, WeightLog
from .serializers import (
    RoutineSerializer,
    RoutineSettingsSerializer,
    ExerciseSerializer,
)

from dateutil.relativedelta import relativedelta
from matplotlib.ticker import MaxNLocator
from django.db.models import Max
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import (
    ExerciseForm,
)
from .forms import WorkoutSettingsForm
from .utils import *
from matplotlib import pyplot as plt
from io import BytesIO
import matplotlib

matplotlib.use("Agg")
from .mixins import ExerciseMixin, WorkoutMixin


def plot_graph(stat_name, values, dates):
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
    plt.savefig(buffer, format="png", transparent=True)
    plt.close()
    buffer.seek(0)

    return buffer.getvalue()


# Create your views here.


class StatsView(ExerciseMixin, TemplateView):
    template_name = "base/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
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
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(
                request, "workout/stats.html", self.get_context_data(**kwargs)
            )
        return super().get(self, request, *args, **kwargs)


class SelectWorkoutView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        try:
            workout = Workout.get_workout(
                self.request.user, self.kwargs["workout_name"]
            )
        except Workout.DoesNotExist:
            return context
        context["workout"] = workout.configure_workout()
        context["workout"]["workout_name"] = self.kwargs["workout_name"]
        context["workout"]["pk"] = workout.pk
        return context


class WorkoutView(WorkoutMixin, TemplateView):
    template_name = "base/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
        context["modules"] = modules

        context["template_content"] = "workout/workout_session.html"

        user_workout_settings, _ = WorkoutSettings.objects.get_or_create(
            user=self.request.user
        )
        context["show_workout_timer"] = user_workout_settings.show_workout_timer
        context["show_rest_timer"] = user_workout_settings.show_rest_timer

        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
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
        context = super().get_context_data(**kwargs)
        exercise = Exercise.get_exercise(self.request.user, self.kwargs["exercise"])
        context["exercise_name"] = exercise.name
        context["sets"] = exercise.sets()

        return context


class AddSetView(LoginRequiredMixin, TemplateView):
    template_name = "workout/set.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        exercise_name = self.kwargs.get("exercise_name")
        exercise = Exercise.get_exercise(self.request.user, exercise_name)
        exercise_set = exercise.set
        context["weight"] = exercise_set["weight"]
        context["reps"] = exercise_set["reps"]

        return context


class WorkoutSettingsView(WorkoutMixin, TemplateView):
    template_name = "workout/workout_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_workout_settings = WorkoutSettings.objects.filter(
            user=self.request.user
        ).first()
        context["form"] = WorkoutSettingsForm(instance=user_workout_settings)
        return context


class WorkoutSettingsSelectWorkoutView(LoginRequiredMixin, TemplateView):
    template_name = "workout/workout_settings_workout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        workout = Workout.get_workout(self.request.user, self.kwargs["workout_name"])
        context["workout"] = workout.config

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

        return context


class WorkoutSettingsAddExerciseView(LoginRequiredMixin, TemplateView):

    template_name = "workout/workout_settings_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise = Exercise.get_exercise(
            self.request.user, self.kwargs["exercise_name"]
        )
        context["exercise"] = exercise

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

            exercise, created = Exercise.objects.get_or_create(
                user=self.request.user, name=exercise["name"]
            )
            if created or exercise not in workout.exercises.all():
                workout.exercises.add(exercise)

        workout.save()

        return JsonResponse({"success": True}, safe=False)


class WorkoutSettingsSaveWorkoutSettingsView(LoginRequiredMixin, FormView):
    model = WorkoutSettings
    form_class = WorkoutSettingsForm

    def form_valid(self, form):
        workout_settings, created = WorkoutSettings.objects.get_or_create(
            user=self.request.user
        )
        workout_settings.auto_update_five_rep_max = form.cleaned_data[
            "auto_update_five_rep_max"
        ]
        workout_settings.show_rest_timer = form.cleaned_data["show_rest_timer"]
        workout_settings.show_workout_timer = form.cleaned_data["show_workout_timer"]
        workout_settings.save()

        return JsonResponse({"success": True}, safe=False)


class ExerciseSettingsView(ExerciseMixin, TemplateView):
    template_name = "workout/exercise_settings.html"


class EditExerciseView(LoginRequiredMixin, FormView):
    form_class = ExerciseForm
    template_name = "workout/edit_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise_name = self.kwargs.get("exercise_name")
        context["exercise"] = Exercise.get_exercise(self.request.user, exercise_name)

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


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            obj.pk = None
            obj.user = request.user
            obj.save()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoutineSettingsView(WorkoutMixin, TemplateView):
    template_name = "workout/routine.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["routines"] = Routine.get_routines(self.request.user)
        context["settings"], _ = RoutineSettings.objects.get_or_create(
            user=self.request.user
        )

        return context


class SaveRoutineSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pass


class SaveRoutineAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RoutineSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            instance = serializer.save()
            data = serializer.data
            data["pk"] = instance.pk
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetRoutineAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoutineSerializer

    def get_queryset(self):
        return Routine.objects.filter(
            Q(user=self.request.user) | Q(user=get_default_user())
        )


class UpdateRoutineSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        obj, created = RoutineSettings.objects.get_or_create(user=user)
        return obj

    def patch(self, request, *args, **kwargs):
        routine_settings = self.get_object()
        serializer = RoutineSettingsSerializer(
            routine_settings, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetActiveWorkoutSearchListView(TemplateView):
    template_name = "workout/active_workout_search_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"], _ = RoutineSettings.objects.get_or_create(
            user=self.request.user
        )

        return context


class GetRoutineWorkoutView(WorkoutMixin, TemplateView):
    template_name = "workout/workout_session.html"

    def get_context_data(self, **kwargs):
        direction = kwargs["direction"]
        routine_settings = RoutineSettings.objects.get(user=self.request.user)

        if direction == "next":
            routine_settings.get_next_workout()
        elif direction == "prev":
            routine_settings.get_prev_workout()
        context = super().get_context_data(**kwargs)
        return context
