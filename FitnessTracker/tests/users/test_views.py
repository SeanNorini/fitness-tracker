from users.models import User
from django.test import TestCase
from django.urls import reverse

USERNAME_VALID = "testuser"
USERNAME_INVALID = "invalid"
PASSWORD_VALID = "testpassword"
PASSWORD_INVALID = "invalid"

REGISTRATION_FORM_FIELDS = {
    "username": "test_name",
    "password": "test_pass123",
    "confirm_password": "test_pass123",
    "first_name": "first",
    "last_name": "last",
    "email": "test_user@gmail.com",
    "gender": "M",
    "weight": "150",
    "height": "75",
    "age": "28",
}


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USERNAME_VALID, password=PASSWORD_VALID
        )
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)

    def test_logout_when_authenticated(self):
        # Make sure the user is initially logged in
        self.assertTrue(self.client.session["_auth_user_id"])

        # Access the logout view
        response = self.client.get(reverse("logout"))

        # Check that the user is logged out
        self.assertFalse("_auth_user_id" in self.client.session)

        # Check the redirect
        self.assertRedirects(response, reverse("login"))

    def test_logout_when_not_authenticated(self):
        # Logout before accessing the view
        self.client.logout()

        # Access the logout view
        response = self.client.get(reverse("logout"))

        # Check that the user remains logged out (no session modification)
        self.assertFalse("_auth_user_id" in self.client.session)

        # Check the redirect
        self.assertRedirects(response, reverse("login"))


class TestLoginView(TestCase):
    fixtures = ["default.json"]

    def test_user_already_authenticated(self):
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)

        response = self.client.get(reverse("login"))

        # Check the redirect
        self.assertRedirects(response, reverse("index"))

    def test_user_not_authenticated(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.resolver_match.view_name, "login")

    def test_valid_form_valid_login(self):
        response = self.client.post(
            reverse("login"),
            data={"username": USERNAME_VALID, "password": PASSWORD_VALID},
        )
        self.assertRedirects(response, reverse("index"))

    def test_valid_form_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            data={"username": USERNAME_INVALID, "password": PASSWORD_INVALID},
        )
        self.assertIn("error", response.context)
        expected_error_message = "Invalid username and/or password."
        self.assertEqual(response.resolver_match.view_name, "login")
        self.assertEqual(response.context["error"], expected_error_message)

    def test_invalid_form(self):
        response = self.client.post(
            reverse("login"),
            data={},
        )
        self.assertIn("error", response.context)
        expected_error_message = "Error. Please try again."
        self.assertEqual(response.resolver_match.view_name, "login")
        self.assertEqual(response.context["error"], expected_error_message)


class TestRegistrationView(TestCase):
    fixtures = ["default.json"]

    def test_user_already_authenticated(self):
        self.client.login(username=USERNAME_VALID, password=PASSWORD_VALID)
        response = self.client.get(reverse("registration"))

        # Check the redirect
        self.assertRedirects(response, reverse("index"))

    def test_user_not_authenticated(self):
        response = self.client.get(reverse("registration"))
        self.assertEqual(response.resolver_match.view_name, "registration")

    def test_valid_registration(self):
        response = self.client.post(
            reverse("registration"),
            data=REGISTRATION_FORM_FIELDS,
        )

        # Check that registration was successful, redirected handled in JS.
        self.assertEqual(response.content.decode("utf-8"), "success")

    def test_invalid_registration(self):
        response = self.client.post(
            reverse("registration"),
            data={},
        )
        self.assertEqual(response.resolver_match.view_name, "registration")
        self.assertTemplateUsed(response, "users/registration_form.html")

        self.assertIn("form", response.context)
        form = response.context["form"]

        # Assert that the form has errors
        self.assertTrue(form.errors)
