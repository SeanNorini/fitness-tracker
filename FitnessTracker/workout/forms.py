from django import forms
from datetime import datetime, timedelta

from django.core.validators import MaxValueValidator
from workout.models import WorkoutLog, Exercise, CardioLog


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


class CardioLogForm(forms.ModelForm):
    # Define form fields
    datetime = forms.DateTimeField()
    duration = forms.DurationField()
    distance = forms.FloatField(min_value=0, max_value=99.99)

    def __init__(self, data=None, *args, **kwargs):
        updated_data = {"datetime": data.get("datetime")}

        duration_hours = int(data.get("duration-hours", 0))
        duration_minutes = int(data.get("duration-minutes", 0))
        duration_seconds = int(data.get("duration-seconds", 0))
        updated_data["duration"] = timedelta(
            hours=duration_hours, minutes=duration_minutes, seconds=duration_seconds
        )

        distance_integer = data.get("distance-integer", 0)
        distance_decimal = data.get("distance-decimal", 0)
        updated_data["distance"] = float(f"{distance_integer}.{distance_decimal}")

        super().__init__(data=updated_data, *args, **kwargs)

    class Meta:
        model = CardioLog
        fields = [
            "datetime",
            "duration",
            "distance",
        ]
