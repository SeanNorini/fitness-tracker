from django import forms
from datetime import datetime
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

    date = forms.DateField()

    time_hours = forms.IntegerField(label="Hours", min_value=1, max_value=12)
    time_minutes = forms.IntegerField(label="Minutes", min_value=0, max_value=59)
    time_period = forms.ChoiceField(
        label="Period", choices=[("AM", "am"), ("PM", "pm")]
    )

    duration_hours = forms.IntegerField(label="Hours", min_value=0, max_value=24)
    duration_minutes = forms.IntegerField(label="Minutes", min_value=0, max_value=59)
    duration_seconds = forms.IntegerField(label="Seconds", min_value=0, max_value=59)

    distance_integer = forms.IntegerField(
        label="Integer Distance", min_value=0, max_value=99
    )
    distance_decimal = forms.IntegerField(
        label="Decimal Distance", min_value=0, max_value=99
    )

    def save(self, commit=True):
        # Perform additional processing before saving
        # Example: Combine distance_integer and distance_decimal into distance
        time_hours = self.cleaned_data.get("time_hours", 0)
        time_minutes = self.cleaned_data.get("time_minutes", 0)
        time_period = self.cleaned_data.get("time_period", "'AM'")

        # Convert 12-hour format to 24-hour format
        if time_period == "PM" and time_hours < 12:
            time_hours += 12
        elif time_period == "AM" and time_hours == 12:
            time_hours = 0

        # Create a datetime object with the date and time components
        time_obj = datetime.strptime(f"{time_hours}:{time_minutes}", "%H:%M").time()

        # Set the time field of the instance
        self.instance.time = time_obj

        distance_integer = self.cleaned_data.get("distance_integer")
        distance_decimal = self.cleaned_data.get("distance_decimal")
        if distance_integer is not None and distance_decimal is not None:
            distance = float(f"{distance_integer}.{distance_decimal}")
            self.instance.distance = distance

        # Call the parent save method to save the data
        return super().save(commit=commit)

    class Meta:
        model = CardioLog
        fields = [
            "date",
            "time_hours",
            "time_minutes",
            "time_period",
            "duration_hours",
            "duration_minutes",
            "duration_seconds",
            "distance_integer",
            "distance_decimal",
        ]
