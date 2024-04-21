from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from users.models import UserSettings
from workout.models import Exercise, Workout, RoutineSettings


class DefaultMixin(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["user_settings"] = UserSettings.get_user_settings(self.request.user.id)
        return context


class ExerciseMixin(DefaultMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["exercises"] = Exercise.get_exercise_list(self.request.user)

        return context


class WorkoutMixin(ExerciseMixin):
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context["workouts"] = Workout.get_workout_list(self.request.user)
        context["routine_settings"], _ = RoutineSettings.objects.get_or_create(
            user=self.request.user
        )
        self.get_routine_context(context)

        return context

    def get_routine_context(self, context) -> dict:
        if context["routine_settings"].routine:
            workout = context["routine_settings"].get_workout()

            if workout:
                context["workout"] = workout.configure_workout()
                context["workout"]["workout_name"] = workout.name
        return context
