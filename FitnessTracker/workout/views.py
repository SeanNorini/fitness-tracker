from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from users.models import User
from .models import Workout, Exercise, WorkoutSettings, Routine, RoutineSettings
from .serializers import (
    RoutineSerializer,
    RoutineSettingsSerializer,
    ExerciseSerializer,
    WorkoutSerializer,
)
from .forms import WorkoutSettingsForm, ExerciseForm
from .base import ExerciseTemplateView, WorkoutTemplateView
from common.base import BaseTemplateView, BaseOwnerViewSet
from common.common_utils import clone_for_user


class WorkoutView(WorkoutTemplateView):
    template_name = "base/index.html"
    fetch_template_name = "workout/workout_session.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["workout_settings"], _ = WorkoutSettings.objects.get_or_create(
            user=self.request.user
        )

        return context


class WorkoutSettingsView(WorkoutTemplateView):
    template_name = "workout/settings/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_workout_settings = WorkoutSettings.objects.filter(
            user=self.request.user
        ).first()
        context["form"] = WorkoutSettingsForm(instance=user_workout_settings)
        return context


class WorkoutViewSet(BaseOwnerViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        configure = self.request.query_params.get("configure")
        if configure:
            data = self.get_serializer(
                instance=instance, context={"configure": True}
            ).data
            return Response(data, status=status.HTTP_200_OK)
        return super().retrieve(request, args, kwargs)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        for exercise in instance.config:
            obj = Exercise.objects.get(name=exercise["name"], user=self.request.user)
            obj.five_rep_max = exercise["five_rep_max"]
            obj.save()


class WorkoutSettingsSaveView(LoginRequiredMixin, FormView):
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


class ExerciseSettingsView(ExerciseTemplateView):
    template_name = "workout/exercise_settings.html"


class EditExerciseView(LoginRequiredMixin, FormView):
    form_class = ExerciseForm
    template_name = "workout/edit_exercise.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise_name = self.kwargs.get("exercise_name")
        context["exercise"] = Exercise.get_exercise(self.request.user, exercise_name)

        return context


class ExerciseViewSet(BaseOwnerViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.is_default:
            clone_for_user(obj, request.user)
            kwargs["pk"] = obj.pk

        return super().update(request, *args, **kwargs)


class RoutineSettingsView(WorkoutTemplateView):
    template_name = "workout/routine.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["routines"] = Routine.get_routines(self.request.user)
        context["settings"], _ = RoutineSettings.objects.get_or_create(
            user=self.request.user
        )

        return context


class RoutineViewSet(BaseOwnerViewSet):
    queryset = Routine.objects.all()
    serializer_class = RoutineSerializer


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


class GetRoutineWorkoutView(WorkoutTemplateView, TemplateView):
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
