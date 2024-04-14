from datetime import timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from common.test_globals import USERNAME_VALID, PASSWORD_VALID
from log.models import WorkoutLog, CardioLog, WorkoutSet
from users.models import User
from workout.models import Workout, Exercise
from datetime import date


class TestWorkoutLogModel(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.get(username="default")
        self.workout = Workout.objects.get(name="Custom Workout")

    def test_user_validation(self):
        test_cases = [
            {"value": None, "error": IntegrityError, "subtest": "User field null"},
            {"value": "", "error": ValidationError, "subtest": "Invalid user value"},
            {"value": self.user, "error": None, "subtest": "Valid user"},
        ]

        for test_case in test_cases:
            with self.subTest(test_case["subtest"]):
                if test_case["error"] is not None:
                    with self.assertRaises(test_case["error"]):
                        WorkoutLog.objects.create(
                            user=test_case["value"],
                            workout=self.workout,
                            date=timezone.now(),
                            total_time=0,
                        )

    def test_workout_validation(self):
        test_cases = [
            {"value": None, "error": IntegrityError, "subtest": "Workout field null"},
            {"value": "", "error": ValidationError, "subtest": "Invalid workout value"},
            {"value": self.workout, "error": None, "subtest": "Valid workout"},
        ]

        for test_case in test_cases:
            with self.subTest(test_case["subtest"]):
                if test_case["error"] is not None:
                    with self.assertRaises(test_case["error"]):
                        WorkoutLog.objects.create(
                            user=self.user,
                            workout=test_case["value"],
                            date=timezone.now(),
                            total_time=0,
                        )

    def test_date_validation(self):
        test_cases = [
            {"value": "", "error": ValidationError, "subtest": "Improper date format"},
            {"value": None, "error": ValidationError, "subtest": "Date cannot be null"},
            {
                "value": date(9999, 2, 14),
                "error": ValidationError,
                "subtest": "Date cannot be in the future",
            },
            {
                "value": date(2019, 1, 13),
                "error": ValidationError,
                "subtest": "Date cannot be more than five years ago",
            },
            {
                "value": timezone.now(),
                "error": None,
                "subtest": "Valid current date",
            },
            {
                "value": timezone.now() - timedelta(days=365 * 5 - 1),
                "error": None,
                "subtest": "Valid max past date",
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case["subtest"]):
                if test_case["error"] is not None:
                    with self.assertRaises(test_case["error"]):
                        WorkoutLog.objects.create(
                            user=self.user,
                            workout=self.workout,
                            date=test_case["date"],
                            total_time=0,
                        )
                else:
                    WorkoutLog.objects.create(
                        user=self.user,
                        workout=self,
                        date=test_case["date"],
                        total_time=0,
                    )
                    self.assertEqual(len(WorkoutLog.objects.all()), 1)

    def test_total_time_validation(self):
        test_cases = [
            {
                "value": timedelta(seconds=-1),
                "error": ValidationError,
                "subtest": "Negative duration",
            },
            {
                "value": timedelta(seconds=0),
                "error": None,
                "subtest": "Min valid duration",
            },
            {
                "value": timedelta(days=1),
                "error": ValidationError,
                "subtest": "Max valid duration",
            },
            {"value": None, "error": ValidationError, "subtest": "Null duration"},
        ]
        for test_case in test_cases:
            with self.subTest(test_case["subtest"]):
                if test_case["error"] is not None:
                    with self.assertRaises(test_case["error"]):
                        WorkoutLog.objects.create(
                            user=self.user,
                            workout=self.workout,
                            date=timezone.now(),
                            total_time=test_case["value"],
                        )
                else:
                    WorkoutLog.objects.create(
                        user=self.user,
                        workout=self,
                        date=timezone.now(),
                        total_time=test_case["value"],
                    )
                    self.assertEqual(len(WorkoutLog.objects.all()), 1)


class TestWorkoutSetModel(TestCase):

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


class CardioLogModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create_user(
            username=USERNAME_VALID, password=PASSWORD_VALID
        )

    def test_datetime_validation(self):
        # Test to ensure the datetime validation is working
        with self.subTest("Invalid future date"):
            cardio_log = CardioLog(
                user=self.user,
                datetime=timezone.now() + timedelta(days=1),  # Future date
                duration=timedelta(minutes=20),
                distance=5.0,
            )
            with self.assertRaises(ValidationError):
                cardio_log.full_clean()

        with self.subTest("Invalid past date"):
            cardio_log = CardioLog(
                user=self.user,
                datetime=timezone.now()
                - timedelta(days=(366 * 5)),  # More than 5 years ago
                duration=timedelta(minutes=20),
                distance=5.0,
            )
            with self.assertRaises(ValidationError):
                cardio_log.full_clean()

        with self.subTest("Valid current date"):
            try:
                cardio_log = CardioLog(
                    user=self.user,
                    datetime=timezone.now() - timedelta(days=((365 * 5) - 1)),
                    duration=timedelta(minutes=20),
                    distance=5.0,
                )
                cardio_log.full_clean()
                cardio_log.save()
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

        with self.subTest("Valid past date"):
            try:
                cardio_log = CardioLog(
                    user=self.user,
                    datetime=timezone.now(),
                    duration=timedelta(minutes=20),
                    distance=5.0,
                )
                cardio_log.full_clean()
                cardio_log.save()
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

    def test_duration_validation(self):
        # Test minimum and maximum duration validation
        with self.subTest("Invalid min duration"):
            cardio_log = CardioLog(
                user=self.user,
                datetime=timezone.now(),
                duration=timedelta(seconds=-1),
                distance=5.0,
            )
            with self.assertRaises(ValidationError):
                cardio_log.full_clean()

        with self.subTest("Invalid max duration"):
            cardio_log = CardioLog(
                user=self.user,
                datetime=timezone.now(),
                duration=timedelta(hours=24) + timedelta(seconds=1),
                distance=5.0,
            )
            with self.assertRaises(ValidationError):
                cardio_log.full_clean()

        with self.subTest("Valid min duration"):
            try:
                cardio_log = CardioLog(
                    user=self.user,
                    datetime=timezone.now(),
                    duration=timedelta(seconds=0),
                    distance=5.0,
                )
                cardio_log.full_clean()
                cardio_log.save()
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

        with self.subTest("Valid max duration"):
            try:
                cardio_log = CardioLog(
                    user=self.user,
                    datetime=timezone.now(),
                    duration=timedelta(hours=24),
                    distance=5.0,
                )
                cardio_log.full_clean()
                cardio_log.save()
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

    def test_distance_validation(self):
        # Test minimum and maximum distance validation
        with self.subTest("Invalid min distance"):
            cardio_log = CardioLog(
                user=self.user,
                datetime=timezone.now() - timedelta(days=1),
                duration=timedelta(minutes=30),
                distance=-1,
            )
            with self.assertRaises(ValidationError):
                cardio_log.full_clean()

        with self.subTest("Invalid max distance"):
            cardio_log = CardioLog(
                user=self.user,
                datetime=timezone.now() - timedelta(days=1),
                duration=timedelta(minutes=30),
                distance=100,
            )
            with self.assertRaises(ValidationError):
                cardio_log.full_clean()

        with self.subTest("Valid min distance"):
            try:
                cardio_log = CardioLog(
                    user=self.user,
                    datetime=timezone.now() - timedelta(days=1),
                    duration=timedelta(minutes=30),
                    distance=0,
                )
                cardio_log.full_clean()
                cardio_log.save()
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

        with self.subTest("Valid max distance"):
            try:
                cardio_log = CardioLog(
                    user=self.user,
                    datetime=timezone.now() - timedelta(days=1),
                    duration=timedelta(minutes=30),
                    distance=99.99,
                )
                cardio_log.full_clean()
                cardio_log.save()
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

    def test_successful_creation(self):
        # Test the successful creation of a valid CardioLog instance
        cardio_log = CardioLog(
            user=self.user,
            datetime=timezone.now(),
            duration=timedelta(minutes=30),
            distance=10.0,
        )
        cardio_log.full_clean()
        cardio_log.save()
        self.assertEqual(CardioLog.objects.count(), 1)
        self.assertEqual(CardioLog.objects.first(), cardio_log)
