from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from log.models import WorkoutLog, WorkoutSet, CardioLog, WeightLog
from workout.models import Exercise, Workout, WorkoutSettings
from users.models import User, UserSettings


class TestWorkoutLog(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.workout = Workout.objects.create(user=self.user, name="Morning Routine")
        self.workout_log = WorkoutLog.objects.create(
            workout=self.workout, user=self.user, date=timezone.now().date()
        )
        self.exercise = Exercise.objects.create(user=self.user, name="Push-ups")
        WorkoutSet.objects.create(
            workout_log=self.workout_log, exercise=self.exercise, weight=50, reps=10
        )

    def test_generate_workout_log(self):
        log = self.workout_log.generate_workout_log()
        self.assertEqual(log["workout_name"], "Morning Routine")
        self.assertEqual(len(log["exercises"]), 1)
        self.assertEqual(log["exercises"][0]["name"], "Push-Ups")
        self.assertEqual(log["exercises"][0]["sets"][0]["reps"], 10)


class TestWorkoutSet(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.workout = Workout.objects.create(user=self.user, name="Evening Routine")
        self.workout_log = WorkoutLog.objects.create(
            workout=self.workout, user=self.user, date=timezone.now().date()
        )
        self.exercise = Exercise.objects.create(user=self.user, name="Sit-Ups")
        self.workout_set = WorkoutSet(
            workout_log=self.workout_log, exercise=self.exercise, weight=70, reps=10
        )

    def test_save_workout_set(self):
        workout_set = WorkoutSet(
            workout_log=self.workout_log, exercise=self.exercise, weight=60, reps=15
        )
        workout_set.save()
        self.assertEqual(WorkoutSet.objects.count(), 1)
        self.assertEqual(WorkoutSet.objects.first().reps, 15)

    @patch("workout.models.Exercise.update_five_rep_max")
    @patch("workout.models.Workout.update_five_rep_max")
    def test_auto_update_five_rep_max(self, mock_update_workout, mock_update_exercise):
        WorkoutSettings.objects.create(user=self.user, auto_update_five_rep_max=True)
        mock_update_exercise.return_value = True

        self.workout_set.save()

        mock_update_exercise.assert_called_once_with(70, 10)

        mock_update_workout.assert_called_once_with(self.exercise)

    def test_no_auto_update_when_setting_is_disabled(self):
        WorkoutSettings.objects.create(user=self.user, auto_update_five_rep_max=False)

        with patch(
            "workout.models.Exercise.update_five_rep_max"
        ) as mock_update_exercise, patch(
            "workout.models.Workout.update_five_rep_max"
        ) as mock_update_workout:
            self.workout_set.save()

            mock_update_exercise.assert_not_called()
            mock_update_workout.assert_not_called()


class CardioLogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="cardiouser")
        self.cardio_log = CardioLog.objects.create(
            user=self.user,
            datetime=timezone.now(),
            duration=timezone.timedelta(minutes=45),
            distance=10,
        )

    def test_get_duration_and_pace(self):
        self.assertEqual(self.cardio_log.get_duration(), "45' 00\"")
        self.assertEqual(self.cardio_log.get_pace(), "4' 30\"")


class WeightLogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="weightuser")
        UserSettings.objects.create(user=self.user, body_weight=70)

    def test_save_weight_log(self):
        weight_log = WeightLog.objects.create(
            user=self.user, body_weight=150, body_fat=20, date=timezone.now().date()
        )
        weight_log.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.body_weight, 150)
        self.assertEqual(self.user.body_fat, 20)
