from django.test import TestCase, Client

from users.models import User


class TestEmailBackend(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username="test", email="test@gmail.com", password="testuser"
        )

    def test_authenticate_by_username(self):
        with self.subTest("Exact username"):
            self.client.login(username="test", password="testuser")
            self.assertTrue(self.user.is_authenticated)
        with self.subTest("Inexact username"):
            self.client.login(username="TeSt", password="testuser")
            self.assertTrue(self.user.is_authenticated)

    def test_authenticate_by_email(self):
        with self.subTest("Exact username"):
            self.client.login(email="test@gmail.com", password="testuser")
            self.assertTrue(self.user.is_authenticated)
        with self.subTest("Inexact username"):
            self.client.login(email="TeSt@gmAiL.com", password="testuser")
            self.assertTrue(self.user.is_authenticated)
