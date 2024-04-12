from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from cardio.models import CardioLog
from common.test_globals import USERNAME_VALID, PASSWORD_VALID
from users.models import User


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
