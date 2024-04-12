from django.test import TestCase
from users.models import User, WeightLog, UserSettings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from common.test_globals import *
from django.utils import timezone


def input_validation(self, model, field_name, field_inputs):
    for field_value in field_inputs["valid"]:
        setattr(model, field_name, field_value)
        model.full_clean()  # Should not raise ValidationError

    for field_value in field_inputs["invalid"]:
        setattr(model, field_name, field_value)
        with self.assertRaises(ValidationError) as context:
            model.full_clean()
        self.assertIn(field_name, context.exception.error_dict)

    return True


class TestUserModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)

    def test_username_validation(self):
        field_inputs = {
            "invalid": [
                "",
                "$invalid_symbol",
                "a" * 151,  # Max length username is 150 by default
            ],
            "valid": ["testusername", "1_test_name_1"],
        }
        assert input_validation(self, self.user, "username", field_inputs)

    def test_email_validation(self):
        field_inputs = {
            "invalid": ["", "a@@gmail.com", "49", "a"],
            "valid": ["test@gmail.com"],
        }
        assert input_validation(self, self.user, "email", field_inputs)

    def test_unique_email(self):
        # Attempt to create a user with an existing email
        with self.assertRaises(IntegrityError):
            User.objects.create(
                username="anotheruser",
                email=self.user.email,  # Use the same email as an existing user
                # Add other required fields here
            )

    def test_first_name_validation(self):
        field_inputs = {
            "invalid": ["", "a", "49", "test_1_name", "f" * 31],
            "valid": ["name", "hi", "f" * 30],
        }
        assert input_validation(self, self.user, "first_name", field_inputs)

    def test_last_name_validation(self):
        field_inputs = {
            "invalid": ["", "a", "49", "test_1_name", "f" * 31],
            "valid": ["name", "hi", "f" * 30],
        }
        assert input_validation(self, self.user, "last_name", field_inputs)

    def test_distance_unit(self):
        user_settings = UserSettings.objects.create(
            user=self.user, system_of_measurement="Imperial"
        )

        distance_unit = self.user.distance_unit()
        self.assertEqual(distance_unit, "mi")

        user_settings.system_of_measurement = "Metric"
        user_settings.save()
        distance_unit = self.user.distance_unit()
        self.assertEqual(distance_unit, "km")

    def test_weight_unit(self):
        user_settings = UserSettings.objects.create(
            user=self.user, system_of_measurement="Imperial"
        )

        weight_unit = self.user.weight_unit()
        self.assertEqual(weight_unit, "Lbs")

        user_settings.system_of_measurement = "Metric"
        user_settings.save()
        weight_unit = self.user.weight_unit()
        self.assertEqual(weight_unit, "Kg")

    def test_get_body_weight(self):
        user_settings = UserSettings.objects.create(user=self.user, body_weight=100)
        body_weight = self.user.get_body_weight()
        self.assertEqual(body_weight, 100)


class TestUserSettingsModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        self.user_settings = UserSettings.objects.create(user=self.user)

    def test_gender_validation(self):
        field_inputs = {
            "invalid": ["", "1", "male"],
            "valid": ["M", "F"],
        }

        assert input_validation(self, self.user_settings, "gender", field_inputs)

    def test_age_validation(self):
        field_inputs = {
            "invalid": ["a", "1.1", "0", "121"],
            "valid": ["1", "120"],
        }
        assert input_validation(self, self.user_settings, "age", field_inputs)

    def test_height_validation(self):
        field_inputs = {
            "invalid": ["a", "19", "271"],
            "valid": ["20", "100.5", "270"],
        }
        assert input_validation(self, self.user_settings, "height", field_inputs)

    def test_body_weight_validation(self):
        field_inputs = {
            "invalid": ["a", "29", "1001"],
            "valid": ["30", "100.5", "1000"],
        }
        assert input_validation(self, self.user_settings, "body_weight", field_inputs)

    def test_body_fat_validation(self):
        field_inputs = {
            "invalid": ["a", "4", "61"],
            "valid": ["5", "60"],
        }
        assert input_validation(self, self.user_settings, "body_fat", field_inputs)

    def test_default_values(self):
        # Verify default values for a new user
        self.assertEqual(self.user_settings.gender, "M")
        self.assertEqual(self.user_settings.height, 70)
        self.assertEqual(self.user_settings.body_weight, 160)
        self.assertEqual(self.user_settings.body_fat, 20)
        self.assertEqual(self.user_settings.age, 30)


class TestWeightLogModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="test@example.com")
        self.date = timezone.localdate()

    def test_create_weight_entry(self):
        # Create a weight entry
        weight_entry = WeightLog.objects.create(
            user=self.user, body_weight=70.5, body_fat=20, date=self.date
        )

        # Check if the weight entry is created successfully
        self.assertIsNotNone(weight_entry)
        self.assertEqual(weight_entry.user, self.user)
        self.assertEqual(weight_entry.body_weight, 70.5)
        self.assertEqual(weight_entry.body_fat, 20)
        self.assertEqual(weight_entry.date, self.date)

    def test_update_existing_weight_entry(self):
        # Create an initial weight entry
        initial_weight_entry, _ = WeightLog.objects.update_or_create(
            user=self.user,
            date=self.date,
            defaults={"body_weight": 70.5, "body_fat": 19},
        )

        # Create another weight entry with the same user and date but different weight
        updated_weight_entry, _ = WeightLog.objects.update_or_create(
            user=self.user,
            date=self.date,
            defaults={"body_weight": 75.0, "body_fat": 20},
        )

        # Refresh the initial weight entry from the database
        initial_weight_entry.refresh_from_db()

        # Check if the initial weight entry is updated with the new weight
        self.assertEqual(initial_weight_entry.body_weight, 75.0)
        self.assertEqual(initial_weight_entry.body_fat, 20)

    def test_unique_together_constraint(self):
        # Create a weight entry
        WeightLog.objects.create(
            user=self.user, body_weight=70.5, body_fat=20, date=self.date
        )

        # Try to create another weight entry with the same user and date
        with self.assertRaises(Exception) as context:
            WeightLog.objects.create(
                user=self.user, body_weight=75.0, body_fat=21, date=self.date
            )

        # Check if the correct exception (IntegrityError) is raised due to the unique constraint
        self.assertTrue("UNIQUE constraint" in str(context.exception))
