from django.contrib.auth.mixins import LoginRequiredMixin

from workout.models import Exercise, Workout, RoutineSettings


class ExerciseMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["exercises"] = Exercise.get_exercise_list(self.request.user)

        return context


class WorkoutMixin(ExerciseMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["workouts"] = Workout.get_workout_list(self.request.user)
        context["routine_settings"], _ = RoutineSettings.objects.get_or_create(
            user=self.request.user
        )
        if context["routine_settings"].routine:
            workout = context["routine_settings"].get_workout()
            print(workout)
            if workout:
                context["workout"] = workout.configure_workout()
                context["workout"]["workout_name"] = workout.name

        return context
