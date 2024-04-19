from unittest import mock

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from datetime import timedelta

from log.models import WeightLog, FoodLog, FoodItem
from log.serializers import (
    WeightLogSerializer,
    CardioLogSerializer,
    FoodItemSerializer,
    FoodLogSerializer,
)
from users.models import User
from common.test_globals import *
from rest_framework.test import APITestCase


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
        instance = serializer.save(user=self.user)
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.duration, timedelta(hours=1))
        self.assertEqual(instance.distance, 10.0)


class TestWeightLogSerializer(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(**CREATE_USER)
        self.weight_log = WeightLog.objects.create(
            user=self.user, body_weight=150, body_fat=18, date=timezone.localdate()
        )

    def test_expected_fields(self) -> None:
        serializer = WeightLogSerializer(instance=self.weight_log)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {"id", "user", "body_weight", "body_fat", "date"},
        )

    def test_weight_log_field_content(self) -> None:
        serializer = WeightLogSerializer(instance=self.weight_log)
        data = serializer.data

        self.assertEqual(data["user"], self.weight_log.user.pk)
        self.assertEqual(data["body_weight"], self.weight_log.body_weight)
        self.assertEqual(data["body_fat"], self.weight_log.body_fat)
        self.assertEqual(data["date"], str(self.weight_log.date))


class TestFoodItemSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.food_log = FoodLog.objects.create(
            user=self.user, date=timezone.localdate()
        )
        self.food_data = {
            "name": "Apple",
            "log_entry": self.food_log,
            "calories": "95",
            "protein": "0.5",
            "carbs": "25",
            "fat": "0.3",
        }

    def test_food_item_valid_data(self):
        serializer = FoodItemSerializer(data=self.food_data)
        self.assertTrue(serializer.is_valid())
        food_item = serializer.save()
        self.assertEqual(food_item.name, "Apple")
        self.assertEqual(food_item.calories, 95)
        self.assertEqual(food_item.protein, 0.5)
        self.assertEqual(food_item.carbs, 25)
        self.assertEqual(food_item.fat, 0.3)

    def test_food_item_invalid_data(self):
        invalid_data = self.food_data.copy()
        invalid_data["calories"] = "abc"  # Invalid calorie input
        serializer = FoodItemSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("calories", serializer.errors)


class TestFoodLogSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="testpassword")
        self.food_log_data = {
            "date": timezone.localdate(),
            "food_items": [
                {
                    "name": "Apple",
                    "calories": 95,
                    "protein": 0.5,
                    "carbs": 25,
                    "fat": 0.3,
                },
                {
                    "name": "Banana",
                    "calories": 105,
                    "protein": 1.3,
                    "carbs": 27,
                    "fat": 0.4,
                },
            ],
        }

    def test_create_food_log_with_items(self):
        serializer = FoodLogSerializer(data=self.food_log_data)
        serializer.context["request"] = mock.MagicMock(user=self.user)
        self.assertTrue(serializer.is_valid())
        food_log = serializer.save(user=self.user)
        self.assertEqual(food_log.food_items.count(), 2)
        self.assertEqual(food_log.user, self.user)

    def test_update_food_log(self):
        food_log = FoodLog.objects.create(user=self.user, date=timezone.localdate())
        FoodItem.objects.create(
            log_entry=food_log,
            name="Old Food",
            calories=200,
            protein=10,
            carbs=20,
            fat=5,
        )
        self.assertEqual(food_log.food_items.count(), 1)

        serializer = FoodLogSerializer(instance=food_log, data=self.food_log_data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        updated_log = serializer.save()
        self.assertEqual(
            updated_log.food_items.count(), 2
        )  # Old item should be removed

    def test_unique_together_constraint(self):
        FoodLog.objects.create(user=self.user, date=timezone.localdate())
        serializer = FoodLogSerializer(data=self.food_log_data)
        serializer.is_valid()
        serializer.save()
        self.assertEqual(len(FoodLog.objects.all()), 1)
