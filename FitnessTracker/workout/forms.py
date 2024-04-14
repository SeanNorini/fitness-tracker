from django import forms
from workout.models import Exercise, WorkoutSettings


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "five_rep_max"]


class WorkoutSettingsForm(forms.ModelForm):
    class Meta:
        model = WorkoutSettings
        fields = ["auto_update_five_rep_max", "show_rest_timer", "show_workout_timer"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["auto_update_five_rep_max"].label = (
            "Update five rep max after workout (Only on increases)"
        )
        self.fields["show_rest_timer"].label = "Show rest timer after set"
        self.fields["show_workout_timer"].label = "Show workout timer"
