from django.test import TestCase
from users.models import User, WeightLog
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from common.test_globals import CREATE_USER


def input_validation(self, field_name, field_inputs):
    for field_value in field_inputs["valid"]:
        setattr(self.user, field_name, field_value)
        self.user.full_clean()  # Should not raise ValidationError

    for field_value in field_inputs["invalid"]:
        setattr(self.user, field_name, field_value)
        with self.assertRaises(ValidationError) as context:
            self.user.full_clean()
        self.assertIn(field_name, context.exception.error_dict)

    return True


class TestUserModel(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)

    def test_gender_validation(self):
        field_inputs = {
            "invalid": ["", "1", "male"],
            "valid": ["M", "F"],
        }

        assert input_validation(self, "gender", field_inputs)

    def test_username_validation(self):
        field_inputs = {
            "invalid": ["", "$invalid_symbol", "too_long" * 20],
            "valid": ["testusername", "1_test_name_1"],
        }
        assert input_validation(self, "username", field_inputs)

    def test_email_validation(self):
        field_inputs = {
            "invalid": ["", "a@@gmail.com", "49", "a"],
            "valid": ["test@gmail.com"],
        }
        assert input_validation(self, "email", field_inputs)

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
        assert input_validation(self, "first_name", field_inputs)

    def test_last_name_validation(self):
        field_inputs = {
            "invalid": ["", "a", "49", "test_1_name", "f" * 31],
            "valid": ["name", "hi", "f" * 30],
        }
        assert input_validation(self, "last_name", field_inputs)

    def test_age_validation(self):
        field_inputs = {
            "invalid": ["", "a", "1.1", "0", "121"],
            "valid": ["1", "120"],
        }
        assert input_validation(self, "age", field_inputs)

    def test_height_validation(self):
        field_inputs = {
            "invalid": ["", "a", "19", "121"],
            "valid": ["20", "100.5", "120"],
        }
        assert input_validation(self, "height", field_inputs)

    def test_weight_validation(self):
        field_inputs = {
            "invalid": ["", "a", "49", "1001"],
            "valid": ["50", "100.5", "1000"],
        }
        assert input_validation(self, "weight", field_inputs)

    def test_default_values(self):
        # Verify default values for a new user
        self.assertEqual(self.user.first_name, "first")
        self.assertEqual(self.user.last_name, "last")
        self.assertEqual(self.user.gender, "M")
        self.assertEqual(self.user.height, 75)
        self.assertEqual(self.user.weight, 150)
        self.assertEqual(self.user.age, 28)


class TestWeightLogModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="test@example.com")
        self.date = timezone.now().date()

    def test_create_weight_entry(self):
        # Create a weight entry
        weight_entry = WeightLog.objects.create(
            user=self.user, weight=70.5, date=self.date
        )

        # Check if the weight entry is created successfully
        self.assertIsNotNone(weight_entry)
        self.assertEqual(weight_entry.user, self.user)
        self.assertEqual(weight_entry.weight, 70.5)
        self.assertEqual(weight_entry.date, self.date)

    def test_update_existing_weight_entry(self):
        # Create an initial weight entry
        initial_weight_entry = WeightLog.objects.create(
            user=self.user, weight=70.5, date=self.date
        )

        # Create another weight entry with the same user and date but different weight
        updated_weight_entry = WeightLog.objects.create(
            user=self.user, weight=75.0, date=self.date
        )

        # Refresh the initial weight entry from the database
        initial_weight_entry.refresh_from_db()

        # Check if the initial weight entry is updated with the new weight
        self.assertEqual(initial_weight_entry.weight, 75.0)

    def test_unique_together_constraint(self):
        # Create a weight entry
        WeightLog.objects.create(user=self.user, weight=70.5, date=self.date)

        # Try to create another weight entry with the same user and date
        with self.assertRaises(Exception) as context:
            WeightLog.objects.create(user=self.user, weight=75.0, date=self.date)

        # Check if the correct exception (IntegrityError) is raised due to the unique constraint
        self.assertTrue("unique constraint" in str(context.exception))
