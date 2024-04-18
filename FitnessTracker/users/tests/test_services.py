from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.core import mail
from unittest.mock import patch
from users.models import User
from users.utils import AccountTokenGenerator, EmailService
import six


class EmailServiceTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="snorini@gmail.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.request = self.factory.get("/test_url")

    def test_send_activation_link_email(self):
        service = EmailService(self.request, self.user)
        service.send_activation_link()

        # Check that one message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct
        self.assertEqual(
            mail.outbox[0].subject, "Fitness Tracker Registration Confirmation"
        )

        # Verify email body is correct
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn("To complete your registration", mail.outbox[0].body)
        self.assertIn("http://", mail.outbox[0].body)

    def test_send_reset_link_email(self):
        service = EmailService(self.request, self.user)
        service.send_reset_link()

        # Check that one message has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct
        self.assertEqual(mail.outbox[0].subject, "Password Reset Request")

        # Verify email body is correct
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn("password reset request was made", mail.outbox[0].body)
        self.assertIn("http://", mail.outbox[0].body)


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
