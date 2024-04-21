from datetime import timedelta
from django.db import IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.test_globals import CREATE_USER
from log.models import (
    WorkoutLog,
    Workout,
    User,
    WorkoutSet,
    WeightLog,
    CardioLog,
    FoodLog,
)
from users.models import UserSettings
from workout.models import WorkoutSettings, Exercise


class TestWorkoutLog(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.workout = Workout.objects.create(name="Test Workout", user=self.user)

    def test_workout_log_creation_valid(self):
        date = timezone.now()
        workout_log = WorkoutLog(workout=self.workout, user=self.user, date=date)
        workout_log.full_clean()
        workout_log.save()
        self.assertEqual(WorkoutLog.objects.count(), 1)

    def test_workout_log_creation_invalid_future_date(self):
        future_date = timezone.now() + timezone.timedelta(days=2)
        workout_log = WorkoutLog(workout=self.workout, user=self.user, date=future_date)
        with self.assertRaises(ValidationError):
            workout_log.full_clean()

    def test_workout_log_creation_invalid_past_date(self):
        past_date = timezone.now() - timezone.timedelta(days=365 * 5 + 2)
        workout_log = WorkoutLog(workout=self.workout, user=self.user, date=past_date)
        with self.assertRaises(ValidationError):
            workout_log.full_clean()

    def test_valid_duration(self):
        duration = timedelta(hours=1)  # 1 hour
        workout_log = WorkoutLog(
            workout=self.workout,
            user=self.user,
            date=timezone.now(),
            total_time=duration,
        )
        try:
            workout_log.full_clean()
        except ValidationError:
            self.fail("Valid duration raised ValidationError unexpectedly!")

    def test_negative_duration(self):
        duration = timedelta(seconds=-1)
        workout_log = WorkoutLog(
            workout=self.workout,
            user=self.user,
            date=timezone.now(),
            total_time=duration,
        )
        with self.assertRaises(ValidationError):
            workout_log.full_clean()

    def test_invalid_duration(self):
        duration = timedelta(days=1, seconds=1)  # 24 hours and 1 second
        workout_log = WorkoutLog(
            workout=self.workout,
            user=self.user,
            date=timezone.now(),
            total_time=duration,
        )
        with self.assertRaises(ValidationError):
            workout_log.full_clean()

    def test_get_logs(self):
        current_year = timezone.now().year
        current_month = timezone.now().month
        workout_log = WorkoutLog.objects.create(
            user=self.user,
            date=timezone.now(),
            workout=self.workout,
            total_time=timezone.timedelta(minutes=30),
        )
        workout_logs = WorkoutLog.get_logs(self.user, current_year, current_month)
        self.assertEqual(workout_logs.count(), 1)
        self.assertEqual(workout_logs.first(), workout_log)


class TestWorkoutSet(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.workout = Workout.objects.create(name="Morning Routine", user=self.user)
        self.exercise = Exercise.objects.create(name="Push-ups", user=self.user)
        self.workout_log = WorkoutLog.objects.create(
            workout=self.workout, user=self.user, date=timezone.now()
        )

        # Settings to automatically update five rep max
        WorkoutSettings.objects.create(user=self.user, auto_update_five_rep_max=True)

    def test_auto_update_five_rep_max_enabled(self):
        """Test the auto update of five rep max when the setting is enabled"""
        initial_five_rep_max = self.exercise.five_rep_max
        workout_set = WorkoutSet(
            workout_log=self.workout_log, exercise=self.exercise, weight=100, reps=5
        )
        workout_set.save()

        self.exercise.refresh_from_db()
        self.assertNotEqual(initial_five_rep_max, self.exercise.five_rep_max)

    def test_auto_update_five_rep_max_disabled(self):
        """Test that five rep max is not updated when the setting is disabled"""
        WorkoutSettings.objects.filter(user=self.user).update(
            auto_update_five_rep_max=False
        )

        initial_five_rep_max = self.exercise.five_rep_max
        workout_set = WorkoutSet(
            workout_log=self.workout_log, exercise=self.exercise, weight=100, reps=5
        )
        workout_set.save()

        self.exercise.refresh_from_db()
        self.assertEqual(initial_five_rep_max, self.exercise.five_rep_max)


class TestCardioLog(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.cardio_log = CardioLog.objects.create(
            user=self.user,
            datetime=timezone.now(),
            duration=timedelta(minutes=30),
            distance=5.0,
        )

    def test_cardio_log_creation(self):
        """Test the creation of a CardioLog instance and validate its methods"""
        self.assertEqual(CardioLog.objects.count(), 1)
        cardio_log = CardioLog.objects.first()
        self.assertEqual(cardio_log.get_duration(), "30' 00\"")
        self.assertEqual(cardio_log.get_pace(), "6' 00\"")

    def test_cardio_log_validation(self):
        """Test the validation rules for past and future dates and duration"""
        with self.assertRaises(ValidationError):
            future_date_log = CardioLog(
                user=self.user,
                datetime=timezone.now() + timedelta(days=1),
                duration=timedelta(minutes=30),
                distance=5.0,
            )
            future_date_log.full_clean()

        with self.assertRaises(ValidationError):
            past_date_log = CardioLog(
                user=self.user,
                datetime=timezone.now() - timedelta(days=5 * 365 + 1),
                duration=timedelta(minutes=30),
                distance=5.0,
            )
            past_date_log.full_clean()

    def test_invalid_distance(self):
        """Test for invalid distance values"""
        with self.assertRaises(ValidationError):
            self.cardio_log.distance = -1
            self.cardio_log.full_clean()

        with self.assertRaises(ValidationError):
            self.cardio_log.distance = 100
            self.cardio_log.full_clean()

    def test_get_logs(self):
        current_year = timezone.now().year
        current_month = timezone.now().month
        cardio_logs = CardioLog.get_logs(self.user, current_year, current_month)
        self.assertEqual(cardio_logs.count(), 1)
        self.assertEqual(cardio_logs.first(), self.cardio_log)


class TestWeightLog(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user_settings = UserSettings.objects.create(user=self.user)
        self.weight_log = WeightLog.objects.create(
            user=self.user, body_weight=175.0, body_fat=15.0, date=timezone.localdate()
        )

    def test_weight_log_creation_and_update(self):
        """Test creation and automatic update upon save"""
        self.assertEqual(self.user_settings.body_weight, 160.0)

        self.assertEqual(WeightLog.objects.count(), 1)
        weight_log = WeightLog.objects.first()
        self.assertEqual(weight_log.body_weight, 175.0)
        self.user_settings = UserSettings.get_user_settings(self.user.id)
        self.assertEqual(self.user_settings.body_weight, 175.0)

        # Check updating and triggering user settings update
        weight_log.body_weight = 180.0
        weight_log.save()
        self.user_settings = UserSettings.get_user_settings(self.user.id)
        self.assertEqual(self.user_settings.body_weight, 180.0)

    def test_unique_constraint(self):
        """Test the unique constraint (one entry per user per date)"""
        with self.assertRaises(IntegrityError):
            duplicate_weight_log = WeightLog.objects.create(
                user=self.user,
                body_weight=180.0,
                body_fat=20.0,
                date=self.weight_log.date,
            )

    def test_get_logs(self):
        current_year = timezone.now().year
        current_month = timezone.now().month
        weight_logs = WeightLog.get_logs(self.user, current_year, current_month)
        self.assertEqual(weight_logs.count(), 1)
        self.assertEqual(weight_logs.first(), self.weight_log)


class TestFoodLog(TestCase):
    def setUp(self):
        self.user = User.objects.create(**CREATE_USER)

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            FoodLog.objects.create(user=self.user, date=timezone.now())
            FoodLog.objects.create(user=self.user, date=timezone.now())
