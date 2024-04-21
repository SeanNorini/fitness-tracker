from django.test import TestCase
from users.models import User, UserSettings
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
        self.assertEqual(self.user_settings.gender, "M")
        self.assertEqual(self.user_settings.height, 70)
        self.assertEqual(self.user_settings.body_weight, 160)
        self.assertEqual(self.user_settings.body_fat, 20)
        self.assertEqual(self.user_settings.age, 30)
