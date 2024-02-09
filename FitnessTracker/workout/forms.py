from django import forms

class WorkoutForm(forms.Form):
    name = forms.CharField(max_length=50)
    exercises = forms.CharField()
    weights = forms.CharField(required=False)
    reps = forms.CharField(required=False)