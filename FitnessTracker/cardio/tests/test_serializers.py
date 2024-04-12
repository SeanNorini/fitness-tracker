from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from datetime import timedelta
from users.models import User
from cardio.models import CardioLog
from cardio.serializers import CardioLogSerializer
from common.test_globals import *


class TestCardioLogSerializer(TestCase):

    def setUp(self):
        self.user = User.objects.create(username=USERNAME_VALID)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_validate_datetime(self):
        test_cases = [
            {
                "value": timezone.now(),
                "valid": True,
            },  # Valid date
            {
                "value": timezone.now() - timedelta(days=5 * 365 - 1),
                "valid": True,
            },  # Valid max past date
            {
                "value": timezone.now() - timedelta(days=5 * 365 + 1),
                "valid": False,
            },  # Invalid max past date
            {
                "value": timezone.now() + timedelta(days=1),
                "valid": False,
            },  # Invalid future date
        ]

        for case in test_cases:
            with self.subTest(case=case):
                if case["valid"]:
                    self.assertEqual(
                        CardioLogSerializer().validate_datetime(case["value"]),
                        case["value"],
                    )
                else:
                    with self.assertRaises(ValidationError):
                        CardioLogSerializer().validate_datetime(case["value"])

    def test_validate_distance(self):
        test_cases = [
            {"value": 0.0, "valid": True},  # Valid min distance
            {
                "value": 99.99,
                "valid": True,
            },  # Valid max distance
            {"value": -0.01, "valid": False},  # Invalid less than min distance
            {"value": 100.0, "valid": False},  # Invalid over max distance
        ]

        for case in test_cases:
            with self.subTest(case=case):
                if case["valid"]:
                    self.assertEqual(
                        CardioLogSerializer().validate_distance(case["value"]),
                        case["value"],
                    )
                else:
                    with self.assertRaises(ValidationError):
                        CardioLogSerializer().validate_distance(case["value"])

    def test_validate_duration(self):
        test_cases = [
            {"value": timedelta(seconds=0), "valid": True},  # Valid min duration
            {
                "value": timedelta(hours=24),
                "valid": True,
            },  # Valid max duration
            {
                "value": timedelta(seconds=-1),
                "valid": False,
            },  # Invalid less than min duration
            {
                "value": timedelta(hours=24, seconds=1),
                "valid": False,
            },  # Invalid over max duration
        ]

        for case in test_cases:
            with self.subTest(case=case):
                if case["valid"]:
                    self.assertEqual(
                        CardioLogSerializer().validate_duration(case["value"]),
                        case["value"],
                    )
                else:
                    with self.assertRaises(ValidationError):
                        CardioLogSerializer().validate_duration(case["value"])

    def test_to_internal_value(self):
        data = {
            "datetime": timezone.now() - timedelta(days=1),
            "duration-hours": 1,
            "duration-minutes": 30,
            "duration-seconds": 0,
            "distance-integer": 5,
            "distance-decimal": 75,
        }
        serializer = CardioLogSerializer(data=data)
        serializer.is_valid()
        internal_data = serializer.validated_data
        self.assertEqual(internal_data["duration"], timedelta(hours=1, minutes=30))
        self.assertAlmostEqual(internal_data["distance"], 5.75)

    def test_create_cardio_log(self):
        data = {
            "datetime": timezone.now() - timedelta(days=1),
            "duration-hours": 1,
            "distance-integer": 10,
        }
        serializer = CardioLogSerializer(data=data, context={"user": self.user})
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.duration, timedelta(hours=1))
        self.assertEqual(instance.distance, 10.0)
