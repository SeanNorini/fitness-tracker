from django import forms

from workout.models import WorkoutLog

from workout.models import Exercise


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
