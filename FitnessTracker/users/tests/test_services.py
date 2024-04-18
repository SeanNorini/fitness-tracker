from django.test.client import RequestFactory
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from users.models import User
from users.services import (
    AccountTokenGenerator,
    EmailService,
    change_user_password,
)
import six


class TestEmailService(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpassword"
        )
        self.request = self.factory.get("/")
        self.request.user = self.user
        self.service = EmailService(self.request, self.user)

    @patch("users.services.get_current_site")
    def test_send_activation_link(self, mock_get_current_site):
        mock_site = MagicMock()
        mock_site.domain = "testserver"
        mock_get_current_site.return_value = mock_site

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            self.service.send_activation_link()
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(
                "Fitness Tracker Registration Confirmation", mail.outbox[0].subject
            )
            self.assertIn(
                "http://{}/user/activate/".format(mock_site.domain), mail.outbox[0].body
            )

    @patch("users.services.get_current_site")
    def test_send_reset_link(self, mock_get_current_site):
        mock_site = MagicMock()
        mock_site.domain = "testserver"
        mock_get_current_site.return_value = mock_site

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            self.service.send_reset_link()
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn("Password Reset Request", mail.outbox[0].subject)
            self.assertIn(
                "http://{}/user/reset_password/".format(mock_site.domain),
                mail.outbox[0].body,
            )

    def test_create_html_body(self):
        html_content = self.service.create_html_body("users/registration_email.html")
        self.assertIn(self.user.username, html_content)


class TestAccountTokenGenerator(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        self.token_generator = AccountTokenGenerator()

    def test_make_hash_value(self):
        # Get the initial timestamp
        timestamp = int(timezone.now().timestamp())

        # Generate the initial hash value
        initial_hash = self.token_generator._make_hash_value(self.user, timestamp)

        # Verify the hash includes the correct user PK, timestamp, and is_active status
        expected_hash = (
            six.text_type(self.user.pk)
            + six.text_type(timestamp)
            + six.text_type(self.user.is_active)
        )
        self.assertEqual(initial_hash, expected_hash)

    def test_hash_changes_with_user_status(self):
        # Get the initial timestamp
        timestamp = int(timezone.now().timestamp())

        # Generate a token for the current user status
        initial_token = self.token_generator.make_token(self.user)

        # Deactivate the user and save
        self.user.is_active = False
        self.user.save()

        # Generate a new token after changing the user status
        new_token = self.token_generator.make_token(self.user)

        # Ensure the token has changed after altering the user's is_active status
        self.assertNotEqual(initial_token, new_token)

    def test_hash_changes_over_time(self):
        # Generate an initial token
        initial_token = self.token_generator.make_token(self.user)

        # Simulate a passage of time by manually altering the timestamp
        future_timestamp = int(timezone.now().timestamp()) + 1

        # Mock _make_hash_value to use the future timestamp
        with patch.object(AccountTokenGenerator, "_make_hash_value") as mock_make_hash:
            mock_make_hash.return_value = self.token_generator._make_hash_value(
                self.user, future_timestamp
            )
            new_token = self.token_generator.make_token(self.user)

        # Ensure a new token is generated over time
        self.assertNotEqual(initial_token, new_token)


class ChangeUserPasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "testuser", "test@test.com", "old_password"
        )

    @patch("users.models.User.check_password")
    @patch("users.models.User.set_password")
    def test_password_change_success(self, mock_set_password, mock_check_password):
        mock_check_password.return_value = True
        mock_set_password.return_value = None

        response = change_user_password(
            self.user, "old_password", "new_password", "new_password"
        )
        mock_check_password.assert_called_once_with("old_password")
        mock_set_password.assert_called_once_with("new_password")
        self.assertEqual(response, {})

    @patch("users.models.User.check_password")
    def test_password_mismatch(self, mock_check_password):
        response = change_user_password(
            self.user, "old_password", "new_password", "different_new_password"
        )
        mock_check_password.assert_not_called()
        self.assertEqual(response, {"confirm_password": ["Passwords don't match"]})

    @patch("users.models.User.check_password")
    def test_incorrect_old_password(self, mock_check_password):
        mock_check_password.return_value = False
        response = change_user_password(
            self.user, "wrong_password", "new_password", "new_password"
        )
        mock_check_password.assert_called_once_with("wrong_password")
        self.assertEqual(response, {"current_password": ["Incorrect password"]})

    @patch("users.models.User.check_password")
    @patch("users.services.validate_password")
    def test_invalid_new_password(self, mock_validate_password, mock_check_password):
        mock_check_password.return_value = True
        mock_validate_password.side_effect = ValidationError(
            ["This password is too short. It must contain at least 8 characters."]
        )

        response = change_user_password(self.user, "old_password", "short", "short")
        mock_validate_password.assert_called_once_with("short", self.user)
        self.assertEqual(
            response,
            {
                "new_password": [
                    "This password is too short. It must contain at least 8 characters."
                ]
            },
        )
