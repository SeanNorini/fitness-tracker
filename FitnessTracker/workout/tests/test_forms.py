from django.test import TestCase
from workout.forms import WorkoutSettingsForm


class TestWorkoutSettingsForm(TestCase):
    def test_form_widgets(self):
        form = WorkoutSettingsForm()
        self.assertIn('id="id_auto_update_five_rep_max"', form.as_p())
        self.assertIn('id="id_show_rest_timer"', form.as_p())
        self.assertIn('id="id_show_workout_timer"', form.as_p())

    def test_missing_fields(self):
        form = WorkoutSettingsForm({})
        self.assertTrue(form.is_valid())
