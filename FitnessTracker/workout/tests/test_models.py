from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import date

from workout.models import *
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
