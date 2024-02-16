from users.models import User
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.utils import account_token_generator
from .test_globals import *
from common.test_utils import (
    form_without_csrf_token,
    form_with_invalid_csrf_token,
    form_with_valid_csrf_token,
)


class TestLoginView(TestCase):
    fixtures = ["default.json"]

    def test_user_already_authenticated(self):
        # Verify redirect on user already logged in
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)

        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def test_user_not_authenticated(self):
        # Verify login page loads
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "login")

    def test_valid_login(self):
        # Verify redirect on valid login
        response = self.client.post(
            reverse("login"),
            data={"username": USERNAME_VALID, "password": PASSWORD_VALID},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

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


class TestLogoutView(TestCase):
    fixtures = ["default.json"]

    def test_user_already_authenticated(self):
        # Verify redirect on user already logged in
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_user_not_authenticated(self):
        # Verify login page loads
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))


class TestRegistrationView(TestCase):
    fixtures = ["default.json"]

    def test_user_already_authenticated(self):
        # Verify authenticated users redirected to index
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)
        response = self.client.get(reverse("registration"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def test_user_not_authenticated(self):
        response = self.client.get(reverse("registration"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "registration")

    def test_valid_registration(self):
        with patch("users.views.send_activation_link") as send_activation_link:
            response = self.client.post(
                reverse("registration"),
                data=REGISTRATION_FORM_FIELDS,
            )
            user = User.objects.get(username=REGISTRATION_FORM_FIELDS["username"])
            # Verify activation link function called
            send_activation_link.assert_called_once_with(response.wsgi_request, user)
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
        status_code = form_without_csrf_token("registration", REGISTRATION_FORM_FIELDS)
        self.assertEqual(status_code, 403)

    def test_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token(
            "registration", REGISTRATION_FORM_FIELDS
        )
        self.assertEqual(status_code, 403)

    def test_valid_csrf_token(self):
        status_code = form_with_valid_csrf_token(
            "registration", REGISTRATION_FORM_FIELDS
        )
        self.assertEqual(status_code, 200)


class TestActivateView(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_name",
            password="testpassword",
            first_name="first",
            last_name="last",
            email="snorini@gmail.com",
            gender="M",
            weight="150",
            height="75",
            age="28",
            is_active=False,
        )

    def test_valid_activation(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        activation_url = reverse("activate", args=[uidb64, token])

        response = self.client.get(activation_url)
        self.user = User.objects.get(username=self.user.username)

        self.assertTrue(self.user.is_active)

    def test_invalid_activation(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = "invalid"
        activation_url = reverse("activate", args=[uidb64, token])

        response = self.client.get(activation_url)
        self.user = User.objects.get(username=self.user.username)

        self.assertFalse(self.user.is_active)
        self.assertTemplateUsed(response, "users/activation_failure.html")


class TestChangePasswordView(TestCase):
    fixtures = ["default.json"]

    def setUp(self) -> None:
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)

    def test_change_password_success(self) -> None:
        response = self.client.post(
            reverse("change_password"), data=CHANGE_PASSWORD_FORM_FIELDS
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "change_password")
        self.assertTemplateUsed(response, "users/change_password_done.html")

    def test_change_password_fail(self) -> None:
        response = self.client.post(reverse("change_password"), data={})
        # Verify page reloads on form error
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "change_password")
        self.assertTemplateUsed(response, "users/change_password_form.html")

        # Verify page has form context with errors
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertTrue(form.errors)

    def test_login_required(self) -> None:
        self.client.logout()
        response = self.client.get(reverse("change_password"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.view_name, "change_password")

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

    def test_valid_csrf_token(self):
        status_code = form_with_valid_csrf_token(
            "change_password", CHANGE_PASSWORD_FORM_FIELDS, login=True
        )
        self.assertEqual(status_code, 200)


class TestResetPasswordView(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.get(username=USERNAME_VALID)

    def test_reset_password_valid_form(self) -> None:
        with patch("users.views.send_reset_link") as send_reset_link:
            response = self.client.post(
                reverse("reset_password"), data={"username": USERNAME_VALID}
            )
            send_reset_link.assert_called_once_with(response.wsgi_request, self.user)
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
        status_code = form_with_valid_csrf_token(
            "reset_password", {"username": USERNAME_VALID}
        )
        self.assertEqual(status_code, 200)


class TestResetPasswordConfirmView(TestCase):
    fixtures = ["default.json"]

    def setUp(self) -> None:
        self.user = User.objects.get(username=LOGIN_USER_FORM_FIELDS["username"])
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_token_generator.make_token(self.user)

    def test_valid_form(self) -> None:
        self.client.get(
            reverse("reset_password_confirm_token", args=[self.uidb64, self.token])
        )
        response = self.client.post(
            reverse("reset_password_confirm"),
            data={"new_password": PASSWORD_VALID, "confirm_password": PASSWORD_VALID},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.resolver_match.view_name, "reset_password_confirm")

    def test_invalid_form(self) -> None:
        response = self.client.get(
            reverse("reset_password_confirm_token", args=[self.uidb64, self.token])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.resolver_match.view_name, "reset_password_confirm_token"
        )
        self.assertTemplateUsed(response, "users/reset_password_change_password.html")

    def test_without_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.get(
            reverse("reset_password_confirm_token", args=[self.uidb64, self.token])
        )
        response = client.post(
            reverse("reset_password_confirm"),
            data={"new_password": PASSWORD_VALID, "confirm_password": PASSWORD_VALID},
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.get(
            reverse("reset_password_confirm_token", args=[self.uidb64, self.token])
        )
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
        client = Client(enforce_csrf_checks=True)
        response = client.get(
            reverse("reset_password_confirm_token", args=[self.uidb64, self.token])
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
        self.assertEqual(response.status_code, 302)
