from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import date

from ..models import *
from users.models import User


MAX_NAME_LENGTH = 100


class TestExerciseModel(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.get(username="default")

    def test_name_not_null(self):
        with self.assertRaises(ValidationError):
            exercise = Exercise.objects.create(user=self.user)
            exercise.full_clean()

        with self.assertRaises(ValidationError):
            exercise = Exercise.objects.create(user=self.user, name="")
            exercise.full_clean()

    def test_name_max_length(self):
        exercise = Exercise.objects.create(user=self.user, name="a" * MAX_NAME_LENGTH)
        exercise.full_clean()

        with self.assertRaises(ValidationError):
            exercise.name = "a" * (MAX_NAME_LENGTH + 1)
            exercise.full_clean()

    def test_user_not_null(self):
        with self.assertRaises(IntegrityError):
            exercise = Exercise.objects.create()

    def test_str_method(self):
        exercise = Exercise.objects.create(user=self.user, name="test")
        self.assertEqual(str(exercise), "test")


class TestWorkoutModel(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.get(username="default")

    def test_name_not_null(self):
        with self.assertRaises(ValidationError):
            workout = Workout.objects.create(user=self.user)
            workout.full_clean()

        with self.assertRaises(ValidationError):
            workout = Workout.objects.create(user=self.user, name="")
            workout.full_clean()

    def test_name_max_length(self):
        workout = Workout.objects.create(
            user=self.user, name="a" * MAX_NAME_LENGTH, config="test"
        )
        workout.full_clean()

        with self.assertRaises(ValidationError):
            workout.name = "a" * (MAX_NAME_LENGTH + 1)
            workout.full_clean()

    def test_user_not_null(self):
        with self.assertRaises(IntegrityError):
            workout = Workout.objects.create(name="a")

    def test_str_method(self):
        workout = Workout.objects.create(user=self.user, name="test")
        self.assertEqual(str(workout), "test")


class TestWorkoutLogModel(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.get(username="default")
        self.workout = Workout.objects.get(name="Custom Workout")

    def test_user_validation(self):
        # user not null
        with self.assertRaises(IntegrityError):
            workoutlog = WorkoutLog.objects.create(workout=self.workout)

    def test_workout_validation(self):
        # workouts not null
        with self.assertRaises(IntegrityError):
            workoutlog = WorkoutLog.objects.create(user=self.user)

    def test_date_validation(self):
        test_cases = [
            ("", ValidationError),  # improper format
            (None, ValidationError),  # Cannot be none
            (date(9999, 2, 14), ValidationError),  # No future dates
            (date(2023, 1, 13), ValidationError),  # No older than 1 year
        ]

        for input, expected_error in test_cases:
            with self.subTest("Testing invalid inputs."):
                try:
                    workoutlog = WorkoutLog(
                        user=self.user, workout=self.workout, date=input
                    )
                    workoutlog.full_clean()
                except Exception as e:
                    self.assertIsInstance(e, expected_error)
                else:
                    self.fail(f"Expected {str(expected_error)}.")


class TestWorkoutSetModel(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.get(username="default")
        self.workout = Workout.objects.create(user=self.user, name="test")
        self.workout_log = WorkoutLog.objects.create(
            workout=self.workout, user=self.user
        )
        self.exercise = Exercise.objects.create(name="test", user=self.user)
        self.set = WorkoutSet(
            workout_log=self.workout_log, exercise=self.exercise, weight=0, reps=0
        )

    def assert_valid_value(self, field, value):
        setattr(self.set, field, value)
        self.set.full_clean()

    def assert_invalid_value(self, field, value):
        with self.assertRaises(ValidationError):
            setattr(self.set, field, value)
            self.set.full_clean()

    def test_exercise_validation(self):
        with self.assertRaises(ValidationError):
            self.set.exercise = None
            self.set.full_clean()

    def test_exercise_validation(self):
        with self.assertRaises(ValidationError):
            self.set.workout_log = None
            self.set.full_clean()

    def test_weight_validation(self):
        with self.subTest("Testing valid min value"):
            self.assert_valid_value("weight", 0)

        with self.subTest("Testing valid max value"):
            self.assert_valid_value("weight", 1500)

        with self.subTest("Testing invalid min value"):
            self.assert_invalid_value("weight", -1)

        with self.subTest("Testing invalid max value"):
            self.assert_invalid_value("weight", 1501)

        with self.subTest("Testing invalid data type"):
            self.assert_invalid_value("weight", "a")

        with self.subTest("Testing missing value"):
            self.assert_invalid_value("weight", None)

    def test_reps_validation(self):
        with self.subTest("Testing valid min value"):
            self.assert_valid_value("reps", 0)

        with self.subTest("Testing valid max value"):
            self.assert_valid_value("reps", 100)

        with self.subTest("Testing invalid min value"):
            self.assert_invalid_value("reps", -1)

        with self.subTest("Testing invalid max value"):
            self.assert_invalid_value("reps", 101)

        with self.subTest("Testing invalid data type"):
            self.assert_invalid_value("reps", "a")

        with self.subTest("Testing missing value"):
            self.assert_invalid_value("reps", None)
