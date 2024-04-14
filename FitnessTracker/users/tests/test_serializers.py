from rest_framework.test import APITestCase, APIRequestFactory
from log.models import WeightLog
from users.serializers import (
    UpdateUserAccountSettingsSerializer,
    UpdateUserSettingsSerializer,
)
from users.models import User, UserSettings
from common.test_globals import *
from django.utils import timezone
from rest_framework.test import APIClient

class UpdateUserAccountSettingsSerializerTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username=USERNAME_VALID, password=PASSWORD_VALID, email=EMAIL_VALID
        )

    def test_email_match_validation(self) -> None:
        # Test data where the confirm_email matches the email
        valid_data = {
            "email": EMAIL_VALID,
            "confirm_email": EMAIL_VALID,
            "first_name": "Test",
            "last_name": "User",
        }

        serializer = UpdateUserAccountSettingsSerializer(
            instance=self.user, data=valid_data
        )
        self.assertTrue(serializer.is_valid())

        # Test data where the confirm_email does not match the email
        invalid_data = valid_data.copy()
        invalid_data["confirm_email"] = "mismatch@gmail.com"

        serializer = UpdateUserAccountSettingsSerializer(
            instance=self.user, data=invalid_data
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("Emails do not match", serializer.errors["confirm_email"])

    def test_expected_fields(self) -> None:
        serializer = UpdateUserAccountSettingsSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {"email", "first_name", "last_name"},
        )

    def test_user_account_field_content(self) -> None:
        serializer = UpdateUserAccountSettingsSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name


class UpdateUserSettingsSerializerTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(**CREATE_USER)
        self.user_settings = UserSettings.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_weight_log_update_on_user_settings_update(self):
        new_weight_data = {
            "user": self.user,
            "system_of_measurement": "Metric",
            "gender": "F",
            "height": 65,
            "body_weight": 150,  # New weight to trigger WeightLog update
            "body_fat": 15,  # New body fat to trigger WeightLog update
            "age": 25,
        }

        context = {"request": self.factory.get("/login/", HTTP_HOST="testserver")}
        context["request"].user = self.user
        serializer = UpdateUserSettingsSerializer(
            instance=self.user_settings,
            data=new_weight_data,
            context=context,
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Verify that a WeightLog entry was created/updated for today
        today_log = WeightLog.objects.filter(
            user=self.user, date=timezone.localdate()
        ).first()
        self.assertIsNotNone(today_log)
        self.assertEqual(today_log.body_weight, 150)
        self.assertEqual(today_log.body_fat, 15)

    def test_expected_fields(self) -> None:
        serializer = UpdateUserSettingsSerializer(instance=self.user_settings)
        data = serializer.data

        self.assertEqual(
            set(data.keys()),
            {
                "system_of_measurement",
                "gender",
                "height",
                "body_weight",
                "body_fat",
                "age",
            },
        )

    def test_weight_log_field_content(self) -> None:
        serializer = UpdateUserSettingsSerializer(instance=self.user_settings)
        data = serializer.data

        self.assertEqual(
            data["system_of_measurement"], self.user_settings.system_of_measurement
        )
        self.assertEqual(data["gender"], self.user_settings.gender)
        self.assertEqual(data["height"], self.user_settings.height)
        self.assertEqual(data["body_weight"], self.user_settings.body_weight)
        self.assertEqual(data["body_fat"], self.user_settings.body_fat)
        self.assertEqual(data["age"], self.user_settings.age)
