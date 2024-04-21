from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta
from unittest.mock import patch
from log.models import WorkoutLog, WorkoutSet, CardioLog, WeightLog, FoodLog, FoodItem
from workout.models import Exercise, Workout, WorkoutSettings
from users.models import User, UserSettings


class TestWorkoutLog(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.workout = Workout.objects.create(user=self.user, name="Morning Routine")
        self.workout_log = WorkoutLog.objects.create(
            workout=self.workout,
            user=self.user,
            date=timezone.now().date(),
            total_time=timedelta(hours=1),
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
    def test_auto_update_five_rep_max(self, mock_update_exercise):
        WorkoutSettings.objects.create(user=self.user, auto_update_five_rep_max=True)
        mock_update_exercise.return_value = True

        self.workout_set.save()

        mock_update_exercise.assert_called_once_with(70, 10)

    def test_no_auto_update_when_setting_is_disabled(self):
        WorkoutSettings.objects.create(user=self.user, auto_update_five_rep_max=False)

        with patch(
            "workout.models.Exercise.update_five_rep_max"
        ) as mock_update_exercise:
            self.workout_set.save()
            mock_update_exercise.assert_not_called()


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
        self.user_settings = UserSettings.objects.create(user=self.user, body_weight=70)

    def test_save_weight_log(self):
        weight_log = WeightLog.objects.create(
            user=self.user, body_weight=150, body_fat=20, date=timezone.now().date()
        )
        weight_log.save()
        self.user_settings = UserSettings.get_user_settings(self.user.id)
        self.assertEqual(self.user_settings.body_weight, 150)
        self.assertEqual(self.user_settings.body_fat, 20)


class FoodLogModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.food_log = FoodLog.objects.create(user=cls.user, date=timezone.localdate())

    def test_string_representation(self):
        self.assertEqual(
            str(self.food_log), f"{self.user.username} - {self.food_log.date}"
        )

    def test_duplicate_food_log(self):
        with self.assertRaises(IntegrityError):
            FoodLog.objects.create(user=self.user, date=self.food_log.date)

    def test_food_log_relationship(self):
        self.assertEqual(self.user.food_logs.first(), self.food_log)


class FoodItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.food_log = FoodLog.objects.create(user=cls.user, date=timezone.localdate())
        cls.food_item = FoodItem.objects.create(
            log_entry=cls.food_log,
            name="Banana",
            calories=100,
            protein=1.1,
            carbs=27.5,
            fat=0.3,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.food_item), "Banana")

    def test_food_item_link_to_log(self):
        self.assertEqual(self.food_item.log_entry, self.food_log)

    def test_decimal_field_limits(self):
        self.food_item.protein = 999.99
        self.food_item.save()
        self.assertEqual(self.food_item.protein, 999.99)

        with self.assertRaises(ValidationError):
            self.food_item.carbs = 1000
            self.food_item.full_clean()

    def test_negative_calories(self):
        self.food_item.calories = -10
        with self.assertRaises(ValidationError):
            self.food_item.full_clean()
