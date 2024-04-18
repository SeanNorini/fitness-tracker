from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
from bs4 import BeautifulSoup
from users.models import User
from users.utils import account_token_generator
from common.test_globals import *
from common.test_utils import (
    form_without_csrf_token,
    form_with_invalid_csrf_token,
    form_with_valid_csrf_token,
)
from users.forms import UpdateAccountForm, UserSettingsForm


class TestUserViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        self.default_user = User.objects.create_user(username="default")
        self.registration = REGISTRATION_FORM_FIELDS


class TestLoginView(TestUserViews):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse("login"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_user_already_authenticated(self):
        with patch(
            "users.models.UserSettings"
        ) as mock:  # Mocked to prevent model does not exist error
            # Verify redirect on user already logged in
            self.client.force_login(self.user)

            response = self.client.get(reverse("login"))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("workout"))

    def test_user_not_authenticated(self):
        # Verify login page loads
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "login")
        self.assertTemplateUsed(response, "users/login.html")

    def test_valid_login(self):
        with patch(
            "users.models.UserSettings"
        ) as mock:  # Mocked to prevent model does not exist error
            # Verify redirect on valid login
            response = self.client.post(
                reverse("login"),
                data=LOGIN_USER_FORM_FIELDS,
            )
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("workout"))

    def test_invalid_login(self):
        # Verify form loads again with field errors
        response = self.client.post(
            reverse("login"),
            data={"username": USERNAME_INVALID, "password": PASSWORD_INVALID},
        )
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "login")

    def test_without_csrf_token(self):
        status_code = form_without_csrf_token("login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(status_code, 403)

    def test_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token("login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(status_code, 403)

    def test_valid_csrf_token(self):
        status_code = form_with_valid_csrf_token("login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(status_code, 302)

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


class TestLogoutView(TestUserViews):
    def test_user_already_authenticated(self):
        # Verify redirect on user already logged in
        self.client.force_login(self.user)

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_user_not_authenticated(self):
        # Verify login page loads
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))


class TestRegistrationView(TestUserViews):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse("registration"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_user_already_authenticated(self):
        with patch(
            "users.models.UserSettings"
        ) as mock:  # Mocked to prevent model does not exist error
            # Verify authenticated users redirected to index
            self.client.force_login(self.user)
            response = self.client.get(reverse("registration"))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("workout"))

    def test_user_not_authenticated(self):
        response = self.client.get(reverse("registration"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "registration")
        self.assertTemplateUsed(response, "users/registration.html")

    def test_valid_registration(self):
        with patch("users.utils.EmailService.send_activation_link") as email_service:
            response = self.client.post(
                reverse("registration"),
                data=REGISTRATION_FORM_FIELDS,
            )
            user = User.objects.get(username=REGISTRATION_FORM_FIELDS["username"])
            # Verify activation link function called
            email_service.assert_called_once()
            # Check that registration was successful, confirmation message displayed.
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.resolver_match.view_name, "registration")
            self.assertTemplateUsed(response, "users/registration_success.html")

    def test_invalid_registration(self):
        # Verify invalid form is returned with errors
        response = self.client.post(
            reverse("registration"),
            data={},
        )
        # Verify page reloads on form error
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "registration")
        self.assertTemplateUsed(response, "users/registration_form.html")

        # Verify page has form context with errors
        self.assertIn("form", response.context)
        form = response.context["form"]

        self.assertTrue(form.errors)

    def test_without_csrf_token(self):
        status_code = form_without_csrf_token(
            "registration", {"username": USERNAME_VALID, "password": PASSWORD_VALID}
        )
        self.assertEqual(status_code, 403)

    def test_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token(
            "registration", {"username": USERNAME_VALID, "password": PASSWORD_VALID}
        )
        self.assertEqual(status_code, 403)

    def test_valid_csrf_token(self):
        with patch(
            "users.utils.EmailService"
        ) as mock:  # mocked to stop EmailService from running
            status_code = form_with_valid_csrf_token(
                "registration", {"username": USERNAME_VALID, "password": PASSWORD_VALID}
            )
            self.assertEqual(status_code, 200)

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


class TestActivateView(TestUserViews):
    def setUp(self):
        super().setUp()
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.url = reverse("activate", args=[uidb64, token])
        self.response = self.client.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_valid_activation(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        activation_url = reverse("activate", args=[uidb64, token])

        response = self.client.get(activation_url)
        user = User.objects.get(username=self.user.username)

        self.assertTrue(user.is_active)
        self.assertTemplateUsed(response, "users/activation_success.html")

    def test_invalid_activation(self) -> None:
        self.user.is_active = False
        self.user.save()
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = "invalid"
        activation_url = reverse("activate", args=[uidb64, token])

        response = self.client.get(activation_url)
        self.user = User.objects.get(username=self.user.username)

        self.assertFalse(self.user.is_active)
        self.assertTemplateUsed(response, "users/activation_failure.html")

    def test_title(self):
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Account Activation")

    def test_links_exist(self):
        home_link = self.soup.find("a", href="/")
        self.assertIsNotNone(home_link, "Home link not found")


class TestChangePasswordFormView(TestUserViews):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_login(self.user)
        self.response = self.client.get(reverse("change_password_form"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_login_required(self) -> None:
        self.client.logout()
        response = self.client.get(reverse("change_password_form"))
        self.assertEqual(response.status_code, 302)

    def test_correct_templated_rendered(self) -> None:
        self.client.get(reverse("change_password_form"))
        self.assertTemplateUsed("users/change_password_form.html")

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


class TestChangePasswordAPIView(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(**CREATE_USER)
        self.default_user = User.objects.create_user(username="default")
        self.client.force_login(self.user)

    def test_change_password_success(self) -> None:
        response = self.client.post(
            reverse("change_password"), data=CHANGE_PASSWORD_FORM_FIELDS
        )
        self.assertEqual(response.status_code, 200)

    def test_change_password_fail(self) -> None:
        response = self.client.post(
            reverse("change_password"), data={"current_password": PASSWORD_INVALID}
        )
        # Verify page reloads on form error
        self.assertEqual(response.status_code, 400)
        self.assertIn("Incorrect password", response.data.get("current_password", []))

    def test_without_csrf_token(self):
        status_code = form_without_csrf_token(
            "change_password", CHANGE_PASSWORD_FORM_FIELDS, login=True
        )
        self.assertEqual(status_code, 403)

    def test_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token(
            "change_password", CHANGE_PASSWORD_FORM_FIELDS, login=True
        )
        self.assertEqual(status_code, 403)

    def test_login_required(self) -> None:
        self.client.logout()
        response = self.client.get(reverse("change_password"))
        self.assertEqual(response.status_code, 403)

    def test_valid_session_id(self):
        with patch(
            "users.models.UserSettings"
        ) as mock:  # Mocked to prevent model does not exist error
            response = self.client.post(
                reverse("change_password"), data=CHANGE_PASSWORD_FORM_FIELDS
            )
            self.assertEqual(response.status_code, 200)


class TestResetPasswordView(TestUserViews):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse("reset_password"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_reset_password_valid_form(self) -> None:
        with patch("users.utils.EmailService.send_reset_link") as email_service:
            response = self.client.post(
                reverse("reset_password"), data={"username": USERNAME_VALID}
            )
            email_service.assert_called_once()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.resolver_match.view_name, "reset_password")
            self.assertTemplateUsed(response, "users/reset_password_request.html")

    def test_reset_password_invalid_form(self) -> None:
        response = self.client.post(reverse("reset_password"), data={"username": "A"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "reset_password")
        self.assertTemplateUsed(response, "users/reset_password_form.html")

    def test_without_csrf_token(self):
        status_code = form_without_csrf_token(
            "reset_password", {"username": USERNAME_VALID}
        )
        self.assertEqual(status_code, 403)

    def test_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token(
            "reset_password", {"username": USERNAME_VALID}
        )
        self.assertEqual(status_code, 403)

    def test_valid_csrf_token(self):
        with patch(
            "users.views.EmailService"
        ) as mock:  # Mocked to prevent EmailService from running
            status_code = form_with_valid_csrf_token(
                "reset_password", {"username": USERNAME_VALID}
            )
            self.assertEqual(status_code, 200)

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


class TestResetPasswordConfirmView(TestUserViews):

    def setUp(self) -> None:
        super().setUp()
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.url = reverse("reset_password_confirm_token", args=[uidb64, token])
        self.response = self.client.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_valid_form(self) -> None:
        response = self.client.post(
            reverse("reset_password_confirm"),
            data={"new_password": PASSWORD_VALID, "confirm_password": PASSWORD_VALID},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "reset_password_confirm")

    def test_invalid_form(self) -> None:
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            self.response.resolver_match.view_name, "reset_password_confirm_token"
        )
        self.assertTemplateUsed(
            self.response, "users/reset_password_change_password.html"
        )

    def test_without_csrf_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("reset_password_confirm_token", args=[uidb64, token]))
        response = client.post(
            reverse("reset_password_confirm"),
            data={"new_password": PASSWORD_VALID, "confirm_password": PASSWORD_VALID},
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_csrf_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("reset_password_confirm_token", args=[uidb64, token]))
        response = client.post(
            reverse("reset_password_confirm"),
            data={
                "new_password": PASSWORD_VALID,
                "confirm_password": PASSWORD_VALID,
                "csrfmiddlewaretoken": "invalid_token",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_valid_csrf_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        client = Client(enforce_csrf_checks=True)
        response = client.get(
            reverse("reset_password_confirm_token", args=[uidb64, token])
        )
        csrf_token = response.context["csrf_token"]
        response = client.post(
            reverse("reset_password_confirm"),
            data={
                "new_password": PASSWORD_VALID,
                "confirm_password": PASSWORD_VALID,
                "csrfmiddlewaretoken": csrf_token,
            },
        )
        self.assertEqual(response.status_code, 200)

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


class TestUserSettingsView(TestUserViews):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.url = reverse("user_settings")
        self.response = self.client.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_fetch_request_template(self):
        response = self.client.get(
            reverse("user_settings"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertTemplateUsed(response, "users/settings.html")

    def test_standard_request_template_and_context(self):
        response = self.client.get(reverse("user_settings"))
        self.assertTemplateUsed(response, "base/index.html")
        self.assertIsInstance(response.context["form"], UpdateAccountForm)
        self.assertIsInstance(response.context["user_settings_form"], UserSettingsForm)
        self.assertIn("modules", response.context)
        self.assertIn("template_content", response.context)
        self.assertEqual(response.context["template_content"], "users/settings.html")

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


class TestDeleteUserView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.url = reverse("delete_account")
        self.client.force_login(self.user)

    def test_delete_user_valid_confirmation(self):
        response = self.client.delete(
            self.url, data={"confirmation": "delete"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username="testuser")

    def test_delete_user_invalid_confirmation(self):
        response = self.client.delete(
            self.url, data={"confirmation": "invalid"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(User.objects.filter(username="testuser").exists())
