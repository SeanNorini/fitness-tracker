from django.core import mail
from django.test import TestCase
from django.contrib.auth.hashers import check_password
from django.test.client import RequestFactory
from users.models import User
from users.services import change_user_password, EmailService
from common.test_globals import CREATE_USER


class ChangeUserPasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test@test.com", "old_password")

    def test_password_change_success(self):
        response = change_user_password(
            self.user, "old_password", "new_password", "new_password"
        )
        self.user.refresh_from_db()
        self.assertTrue(check_password("new_password", self.user.password))
        self.assertEqual(response, {})

    def test_password_mismatch(self):
        response = change_user_password(
            self.user, "old_password", "new_password", "different_new_password"
        )
        self.assertEqual(response, {"confirm_password": ["Passwords don't match"]})

    def test_incorrect_old_password(self):
        response = change_user_password(
            self.user, "wrong_password", "new_password", "new_password"
        )
        self.assertEqual(response, {"current_password": ["Incorrect password"]})

    def test_invalid_new_password(self):
        response = change_user_password(self.user, "old_password", "short", "short")
        self.assertEqual(
            response,
            {
                "new_password": [
                    "This password is too short. It must contain at least 8 characters."
                ]
            },
        )


class EmailServiceTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(**CREATE_USER)
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
