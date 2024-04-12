from django.core.exceptions import ObjectDoesNotExist
from rest_framework.test import APITestCase

from users.models import User
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
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


class TestActivateView(TestUserViews):

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


class TestChangePasswordFormView(TestUserViews):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_login(self.user)

    def test_login_required(self) -> None:
        self.client.logout()
        response = self.client.get(reverse("change_password_form"))
        self.assertEqual(response.status_code, 302)

    def test_correct_templated_rendered(self) -> None:
        self.client.get(reverse("change_password_form"))
        self.assertTemplateUsed("users/change_password_form.html")


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


class TestResetPasswordConfirmView(TestUserViews):

    def setUp(self) -> None:
        super().setUp()
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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)


class TestUserSettingsView(TestUserViews):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

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


class TestDeleteUserView(TestUserViews):
    def test_delete_user(self):
        self.client.force_login(self.user)
        self.client.get(reverse("delete_account"))
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username=USERNAME_VALID)
