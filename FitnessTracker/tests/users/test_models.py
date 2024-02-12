from django.test import TestCase
from users.models import User
from django.core.exceptions import ValidationError


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
        self.user = User.objects.get(username="testuser")

    def test_gender_field(self):
        field_inputs = {
            "invalid": ["", "1", "male"],
            "valid": ["M", "F"],
        }

        assert input_validation(self, "gender", field_inputs)

    def test_username_field(self):
        field_inputs = {
            "invalid": ["", "$invalid_symbol", "too_long" * 20],
            "valid": ["testusername", "1_test_name_1"],
        }
        assert input_validation(self, "username", field_inputs)

    def test_email_field(self):
        field_inputs = {
            "invalid": ["", "a@@gmail.com", "49", "a"],
            "valid": ["test@gmail.com"],
        }
        assert input_validation(self, "email", field_inputs)

    def test_first_name_field(self):
        field_inputs = {
            "invalid": ["", "a", "49", "test_1_name", "f" * 31],
            "valid": ["name", "hi", "f" * 30],
        }
        assert input_validation(self, "first_name", field_inputs)

    def test_last_name_field(self):
        field_inputs = {
            "invalid": ["", "a", "49", "test_1_name", "f" * 31],
            "valid": ["name", "hi", "f" * 30],
        }
        assert input_validation(self, "last_name", field_inputs)

    def test_age_field(self):
        field_inputs = {
            "invalid": ["", "a", "1.1", "0", "121"],
            "valid": ["1", "120"],
        }
        assert input_validation(self, "age", field_inputs)

    def test_height_field(self):
        field_inputs = {
            "invalid": ["", "a", "19", "121"],
            "valid": ["20", "100.5", "120"],
        }
        assert input_validation(self, "height", field_inputs)

    def test_weight_field(self):
        field_inputs = {
            "invalid": ["", "a", "49", "1001"],
            "valid": ["50", "100.5", "1000"],
        }
        assert input_validation(self, "weight", field_inputs)
