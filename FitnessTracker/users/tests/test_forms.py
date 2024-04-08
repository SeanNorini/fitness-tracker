from django.test import TestCase
from users.forms import *
from common.test_globals import *
from django import forms


class TestGetUsernameField(TestCase):
    def setUp(self):
        self.form = LoginForm()
        self.field = self.form.fields["username"]

    def test_field_attrs(self):
        self.assertEqual(self.field.min_length, MIN_LENGTH_NAME)
        self.assertEqual(self.field.max_length, MAX_LENGTH_USERNAME_OR_EMAIL)
        self.assertEqual(self.field.label, "Username or Email")
        self.assertEqual(self.field.widget.attrs["id"], "username")
        self.assertEqual(self.field.widget.attrs["name"], "username")
        self.assertEqual(self.field.widget.attrs["maxlength"], "254")
        self.assertTrue(self.field.widget.attrs["autofocus"])
        self.assertTrue(self.field.required)

    def test_valid_min_value(self):
        form = LoginForm({"username": "A" * MIN_LENGTH_NAME})
        form.is_valid()
        self.assertNotIn("username", self.form.errors)

    def test_valid_max_value(self):
        form = LoginForm({"username": "A" * MAX_LENGTH_USERNAME_OR_EMAIL})
        form.is_valid()
        self.assertNotIn("username", self.form.errors)

    def test_invalid_min_value(self):
        form = LoginForm({"username": "A" * (MIN_LENGTH_NAME - 1)})
        form.is_valid()
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at least 2 characters (it has 1)."],
        )

    def test_invalid_max_value(self):
        form = LoginForm({"username": "A" * (MAX_LENGTH_USERNAME_OR_EMAIL + 1)})
        form.is_valid()
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at most 254 characters (it has 255)."],
        )

    def test_missing_required_values(self):
        form = LoginForm({})
        form.is_valid()
        self.assertEqual(form.errors["username"], ["This field is required."])


class TestGetPasswordField(TestCase):
    def setUp(self):
        self.form = LoginForm()
        self.field = self.form.fields["password"]

    def test_field_attrs(self):
        self.assertEqual(self.field.min_length, MIN_LENGTH_PASSWORD)
        self.assertEqual(self.field.max_length, MAX_LENGTH_NAME_OR_PASSWORD)
        self.assertEqual(self.field.label, "Password")
        self.assertEqual(self.field.widget.attrs["id"], "password")
        self.assertEqual(self.field.widget.attrs["name"], "password")
        self.assertEqual(self.field.widget.attrs["maxlength"], "100")
        self.assertTrue(self.field.required)

    def test_valid_min_value(self):
        form = LoginForm({"password": "A" * MIN_LENGTH_PASSWORD})
        form.is_valid()
        self.assertNotIn("password", self.form.errors)

    def test_valid_max_value(self):
        form = LoginForm({"password": "A" * MAX_LENGTH_NAME_OR_PASSWORD})
        form.is_valid()
        self.assertNotIn("password", self.form.errors)

    def test_invalid_min_value(self):
        form = LoginForm({"password": "A" * (MIN_LENGTH_PASSWORD - 1)})
        form.is_valid()
        self.assertEqual(
            form.errors["password"],
            ["Ensure this value has at least 8 characters (it has 7)."],
        )

    def test_invalid_max_value(self):
        form = LoginForm({"password": "A" * (MAX_LENGTH_NAME_OR_PASSWORD + 1)})
        form.is_valid()
        self.assertEqual(
            form.errors["password"],
            ["Ensure this value has at most 100 characters (it has 101)."],
        )

    def test_missing_required_values(self):
        form = LoginForm({})
        form.is_valid()
        self.assertEqual(form.errors["password"], ["This field is required."])


class TestLoginForm(TestCase):
    def test_form_widgets(self):
        form = LoginForm()
        self.assertIn('id="username"', form.as_p())
        self.assertIn('id="password"', form.as_p())
        self.assertIn('id="remember_me"', form.as_p())

    def test_remember_me(self):
        form = LoginForm()
        remember_me_id = form.fields["remember_me"].widget.attrs["id"]
        self.assertEqual(remember_me_id, "remember_me")
        self.assertIsInstance(form.fields["remember_me"].widget, forms.CheckboxInput)
        self.assertFalse(form.fields["remember_me"].required)


class TestSetPasswordForm(TestCase):
    def test_form_widgets(self):
        form = SetPasswordForm()
        self.assertIn('id="new_password"', form.as_p())
        self.assertIn('id="confirm_password"', form.as_p())

    def test_passwords_dont_match(self):
        form = SetPasswordForm(
            {"new_password": "valid_pass", "confirm_password": "invalid_pass"}
        )
        form.is_valid()
        self.assertEqual(
            form.errors["new_password"],
            ["Passwords don't match. Please try again."],
        )


class TestResetPasswordForm(TestCase):
    def test_form_widgets(self):
        form = ResetPasswordForm()
        self.assertIn('id="username"', form.as_p())


class TestChangePasswordForm(TestCase):
    def test_form_widgets(self):
        form = ChangePasswordForm()
        self.assertIn('id="current_password"', form.as_p())
        self.assertIn('id="new_password"', form.as_p())
        self.assertIn('id="confirm_password"', form.as_p())


class TestRegistrationForm(TestCase):
    def test_form_widgets(self):
        form = RegistrationForm()
        self.assertIn('id="username"', form.as_p())
        self.assertIn('id="password"', form.as_p())
        self.assertIn('id="confirm_password"', form.as_p())
        self.assertIn('id="first_name"', form.as_p())
        self.assertIn('id="last_name"', form.as_p())
        self.assertIn('id="email"', form.as_p())

    def test_valid_data(self):
        form = RegistrationForm(data=REGISTRATION_FORM_FIELDS)
        self.assertTrue(form.is_valid())

    def test_valid_min_values(self):
        form_data = {
            "username": "A" * MIN_LENGTH_NAME,
            "password": "A" * MIN_LENGTH_PASSWORD,
            "confirm_password": "A" * MIN_LENGTH_PASSWORD,
            "first_name": "f",
            "last_name": "l",
            "email": "s@gmail.com",
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_max_values(self):
        form_data = {
            "username": "A" * MAX_LENGTH_NAME_OR_PASSWORD,
            "password": "A" * MAX_LENGTH_NAME_OR_PASSWORD,
            "confirm_password": "A" * MAX_LENGTH_NAME_OR_PASSWORD,
            "first_name": "A" * MAX_LENGTH_NAME_OR_PASSWORD,
            "last_name": "A" * MAX_LENGTH_NAME_OR_PASSWORD,
            "email": "A" * MAX_LENGTH_NAME_OR_PASSWORD,
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_min_values(self):
        form_data = {
            "username": "A",
            "password": "A" * (MIN_LENGTH_PASSWORD - 1),
            "confirm_password": "A" * (MIN_LENGTH_PASSWORD - 1),
            "first_name": "A",
            "last_name": "A",
            "email": "s@gmail.com",
        }
        form = RegistrationForm(data=form_data)
        expected_errors = {
            "username": ["Ensure this value has at least 2 characters (it has 1)."],
            "password": ["Ensure this value has at least 8 characters (it has 7)."],
            "confirm_password": [
                "Ensure this value has at least 8 characters (it has 7)."
            ],
            "first_name": ["Ensure this value has at least 2 characters (it has 1)."],
            "last_name": ["Ensure this value has at least 2 characters (it has 1)."],
        }
        self.assertDictEqual(form.errors, expected_errors)

    def test_invalid_max_values(self):
        form_data = {
            "username": "A" * (MAX_LENGTH_USERNAME_OR_EMAIL + 1),
            "password": "A" * (MAX_LENGTH_NAME_OR_PASSWORD + 1),
            "confirm_password": "A" * (MAX_LENGTH_NAME_OR_PASSWORD + 1),
            "first_name": "A" * (MAX_LENGTH_NAME_OR_PASSWORD + 1),
            "last_name": "A" * (MAX_LENGTH_NAME_OR_PASSWORD + 1),
            "email": "A" * (MAX_LENGTH_USERNAME_OR_EMAIL - 9) + "@gmail.com",
        }
        form = RegistrationForm(data=form_data)
        expected_errors = {
            "username": ["Ensure this value has at most 254 characters (it has 255)."],
            "password": ["Ensure this value has at most 100 characters (it has 101)."],
            "confirm_password": [
                "Ensure this value has at most 100 characters (it has 101)."
            ],
            "first_name": [
                "Ensure this value has at most 100 characters (it has 101)."
            ],
            "last_name": ["Ensure this value has at most 100 characters (it has 101)."],
            "email": ["Ensure this value has at most 254 characters (it has 255)."],
        }
        self.assertDictEqual(form.errors, expected_errors)

    def test_missing_required_values(self):
        form = RegistrationForm(data={})
        expected_errors = {
            "username": ["This field is required."],
            "password": ["This field is required."],
            "confirm_password": ["This field is required."],
            "email": ["This field is required."],
        }
        self.assertDictEqual(form.errors, expected_errors)

    def test_passwords_dont_match(self):
        form = RegistrationForm(
            {"password": "valid_pass", "confirm_password": "invalid_pass"}
        )
        form.is_valid()
        self.assertEqual(
            form.errors["confirm_password"],
            ["Passwords don't match."],
        )

    def test_default_values(self):
        form_data = {
            "username": "A",
            "password": "A" * (MIN_LENGTH_PASSWORD - 1),
            "confirm_password": "A" * (MIN_LENGTH_PASSWORD - 1),
            "first_name": "",
            "last_name": "",
            "email": "s@gmail.com",
        }
        form = RegistrationForm(form_data)
        form.is_valid()


class TestUserBodyCompositionForm(TestCase):
    def test_form_widgets(self):
        form = UserBodyCompositionForm()
        self.assertIn('id="gender"', form.as_p())
        self.assertIn('id="height"', form.as_p())
        self.assertIn('id="body_weight"', form.as_p())
        self.assertIn('id="age"', form.as_p())
