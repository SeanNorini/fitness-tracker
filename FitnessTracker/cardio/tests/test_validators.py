from datetime import timedelta

from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError
from cardio.validators import (
    validate_not_future_date,
    validate_not_more_than_5_years_ago,
    validate_duration_min,
    validate_duration_max,
)


class TestValidators(TestCase):
    def setUp(self):
        self.date = timezone.now()

    def test_not_future_date(self):
        with self.subTest("Invalid future date"):
            with self.assertRaises(ValidationError):
                validate_not_future_date(self.date + timedelta(days=1))

        with self.subTest("Valid date"):
            try:
                validate_not_future_date(self.date)
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

    def test_not_more_than_5_years(self):
        with self.subTest("Invalid past date"):
            with self.assertRaises(ValidationError):
                validate_not_more_than_5_years_ago(
                    self.date - timedelta(days=((365 * 5) + 1))
                )

        with self.subTest("Valid date"):
            try:
                validate_not_future_date(self.date)
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

    def test_duration_min(self):
        with self.subTest("Invalid min duration"):
            with self.assertRaises(ValidationError):
                validate_duration_min(timedelta(seconds=-1))
        with self.subTest("Valid min duration"):
            try:
                validate_duration_min(timedelta(seconds=0))
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")

    def test_duration_max(self):
        with self.subTest("Invalid max duration"):
            with self.assertRaises(ValidationError):
                validate_duration_max(timedelta(seconds=86401))  # 1 day and 1 second

        with self.subTest("Valid max duration"):
            try:
                validate_duration_max(timedelta(seconds=86400))
            except ValidationError:
                self.fail("Validation error unexpectedly raised!")
