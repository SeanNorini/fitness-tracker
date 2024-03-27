from django.contrib.auth.mixins import LoginRequiredMixin

from workout.models import Exercise, Workout


class ExerciseMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["exercises"] = Exercise.get_exercise_list(self.request.user)

        return context


class WorkoutMixin(ExerciseMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["workouts"] = Workout.get_workout_list(self.request.user)

        return context
