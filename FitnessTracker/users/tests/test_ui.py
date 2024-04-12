from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.models import User
from common.test_globals import *
from django.test import TestCase

from ..utils import account_token_generator
from bs4 import BeautifulSoup


class TestLoginUI(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("login"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_elements_exist(self):
        # Test for the existence of elements by ID
        username = self.soup.find(id="username")
        password = self.soup.find(id="password")
        remember_me = self.soup.find(id="remember_me")
        login = self.soup.find(id="login")

        self.assertIsNotNone(username, "Input with id='username' not found")
        self.assertIsNotNone(password, "Input with id='password' not found")
        self.assertIsNotNone(remember_me, "Checkbox with id='remember_me' not found")
        self.assertIsNotNone(login, "Button with id='login' not found")

    def test_title(self):
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Login")

    def test_links_exist(self):
        # Check for the presence of specific links in the HTML response
        registration_link = self.soup.find(href="/user/registration/")
        reset_password_link = self.soup.find(href="/user/reset_password/")

        self.assertIsNotNone(registration_link, "Registration link not found")
        self.assertIsNotNone(reset_password_link, "Reset password link not found")


class TestRegistrationUI(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("registration"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_elements_exist(self):
        for field_name in REGISTRATION_FORM_FIELDS.keys():
            field = self.soup.find(id=field_name)
            self.assertIsNotNone(field, f"Field '{field_name}' not found")
        register = self.soup.find(attrs={"name": "register"})
        self.assertIsNotNone(register, "Registration button not found")

    def test_title(self):
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Registration")

    def test_links_exist(self):
        login_link = self.soup.find("a", href="/user/login/")
        self.assertIsNotNone(login_link, "Login link not found")


class TestActivateUI(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.url = reverse("activate", args=[uidb64, token])
        self.response = self.client.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_title(self):
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Account Activation")

    def test_links_exist(self):
        home_link = self.soup.find("a", href="/")
        self.assertIsNotNone(home_link, "Home link not found")


class TestResetPasswordUI(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("reset_password"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_title(self):
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Reset Password")

    def test_links_exist(self):
        login_link = self.soup.find("a", href="/user/login/")
        self.assertIsNotNone(login_link, "Login link not found")

    def test_elements_exist(self):
        username_field = self.soup.find(id="username")
        reset_password_button = self.soup.find(id="reset-password")
        self.assertIsNotNone(username_field, "Username input not found")
        self.assertIsNotNone(reset_password_button, "Reset password button not found")


class TestResetPasswordChangePasswordUI(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.url = reverse("reset_password_confirm_token", args=[uidb64, token])
        self.response = self.client.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_title(self):
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Change Password")

    def test_links_exist(self):
        login_link = self.soup.find("a", href="/user/login/")
        self.assertIsNotNone(login_link, "Login link not found")

    def test_elements_exist(self):
        fields = ["new_password", "confirm_password"]
        for field in fields:
            input_field = self.soup.find(id=field)
            self.assertIsNotNone(input_field, f"{field} input not found")
        change_password_button = self.soup.find(attrs={"name": "change-password"})
        self.assertIsNotNone(change_password_button, "Change password button not found")


class TestChangePasswordUI(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        self.client.login(**LOGIN_USER_FORM_FIELDS)
        self.response = self.client.get(reverse("change_password_form"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_links_exist(self):
        settings_link = self.soup.find(id="return-to-settings")
        self.assertIsNotNone(settings_link, "Settings link not found")

    def test_elements_exist(self):
        fields = ["current_password", "new_password", "confirm_password"]
        for field in fields:
            input_field = self.soup.find(attrs={"name": field})
            self.assertIsNotNone(input_field, f"{field} input not found")
        change_password_button = self.soup.find(id="change-password")
        self.assertIsNotNone(change_password_button, "Change password button not found")


class TestUserSettingsUI(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        self.client.login(**LOGIN_USER_FORM_FIELDS)
        self.url = reverse("user_settings")
        self.response = self.client.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_elements_exist(self):
        fields = [
            "first_name",
            "last_name",
            "email",
            "confirm_email",
            "system_of_measurement",
            "gender",
            "age",
            "height",
            "body_weight",
            "body_fat",
        ]
        for field in fields:
            input_field = self.soup.find(id=field)
            self.assertIsNotNone(input_field, f"{field} input not found")

        buttons = [
            "update-account",
            "delete-account",
            "change-password",
            "update-user-settings",
        ]
        for button in buttons:
            btn = self.soup.find(id=button)
            self.assertIsNotNone(btn, f"{button} input not found")
