from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Workout, Exercise, WorkoutSettings, Routine, RoutineSettings
from .serializers import (
    RoutineSerializer,
    RoutineSettingsSerializer,
    ExerciseSerializer,
    WorkoutSerializer,
    WorkoutSettingsSerializer,
)
from .forms import WorkoutSettingsForm, ExerciseForm
from .base import ExerciseTemplateView, WorkoutTemplateView
from common.base import BaseOwnerViewSet
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


class WorkoutSettingsView(WorkoutTemplateView):
    template_name = "workout/settings/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_workout_settings = WorkoutSettings.objects.filter(
            user=self.request.user
        ).first()
        context["form"] = WorkoutSettingsForm(instance=user_workout_settings)
        return context


class WorkoutSettingsViewSet(BaseOwnerViewSet):
    queryset = WorkoutSettings.objects.all()
    serializer_class = WorkoutSettingsSerializer

    def get_object(self):
        return WorkoutSettings.objects.get(user=self.request.user)

    @action(detail=False, methods=["PUT", "PATCH"])
    def update_settings(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance=instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            print(request.data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExerciseSettingsView(ExerciseTemplateView):
    template_name = "workout/exercise_settings.html"


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


class RoutineSettingsViewSet(BaseOwnerViewSet):
    queryset = RoutineSettings.objects.all()
    serializer_class = RoutineSettingsSerializer

    @action(detail=False, methods=["get"])
    def next_workout(self, request):
        routine_settings = RoutineSettings.objects.get(user=request.user)
        next_workout = routine_settings.get_next_workout()
        data = self.get_workout_data(routine_settings, next_workout)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def previous_workout(self, request):
        routine_settings = RoutineSettings.objects.get(user=request.user)
        previous_workout = routine_settings.get_previous_workout()
        data = self.get_workout_data(routine_settings, previous_workout)
        return Response(data, status=status.HTTP_200_OK)

    def get_workout_data(self, settings_instance, workout_instance):
        serializer = WorkoutSerializer(
            instance=workout_instance, context={"configure": True}
        )
        data = serializer.data
        data.update(
            {
                "routine_name": settings_instance.routine.name,
                "week": settings_instance.week_number,
                "day": settings_instance.day_number,
            }
        )
        return data


class GetActiveWorkoutSearchListView(TemplateView):
    template_name = "workout/active_workout_search_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"], _ = RoutineSettings.objects.get_or_create(
            user=self.request.user
        )

        return context
