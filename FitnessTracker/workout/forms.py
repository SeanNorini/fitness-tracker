from django import forms


class WorkoutForm(forms.Form):
    name = forms.CharField(max_length=50)
    exercises = forms.JSONField()
