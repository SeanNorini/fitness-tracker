from django import forms
from datetime import datetime, timedelta

from django.core.validators import MaxValueValidator
from workout.models import WorkoutLog, Exercise, WorkoutSettings


class WorkoutLogForm(forms.ModelForm):
    date = forms.DateField()
    workout_name = forms.CharField(max_length=50)
    exercises = forms.JSONField()
    total_time = forms.IntegerField()

    class Meta:
        model = WorkoutLog
        fields = ("date", "total_time")


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "five_rep_max", "default_weight", "default_reps"]


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
