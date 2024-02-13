import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import IntegrityError
from django.test import TestCase
from selenium import webdriver
from unittest.mock import patch
from users.models import User
from common.selenium_utils import *
from common.test_utils import (
    form_without_csrf_token,
    form_with_invalid_csrf_token,
    form_with_valid_csrf_token,
)

REGISTRATION_FORM_FIELDS = {
    "username": "test_name",
    "password": "testpassword",
    "confirm_password": "testpassword",
    "first_name": "first",
    "last_name": "last",
    "email": "test_user@gmail.com",
    "gender": "m",
    "weight": "150",
    "height": "75",
    "age": "28",
}


# Create your tests here.
class TestRegistrationUI(StaticLiveServerTestCase):
    fixtures = ["default.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.driver.get(self.live_server_url + "/user/registration")

    def test_registration_successful(self):
        # Confirm user does not exist
        if len(User.objects.filter(username=REGISTRATION_FORM_FIELDS["username"])) > 0:
            raise IntegrityError

        with patch("users.views.send_activation_link") as send_activation_link:
            fill_form(self.driver, REGISTRATION_FORM_FIELDS)
            click(self.driver, "name", "register")
            time.sleep(1)

            assert User.objects.get(username=REGISTRATION_FORM_FIELDS["username"])
            form_header = find_element(
                self.driver, "id", "registration_confirmation_header"
            ).text
            self.assertEqual(
                form_header,
                f"Thank you for registering, {REGISTRATION_FORM_FIELDS['first_name']}!",
            )

    def test_registration_elements_exist(self) -> None:
        elements = {"name": REGISTRATION_FORM_FIELDS.keys()}
        assert elements_exist(self.driver, elements)

    def test_registration_required_fields(self):
        required_fields = ["username", "password", "confirm_password", "email"]
        assert validate_required_fields(
            self.driver, "registration_form", required_fields
        )


class TestRegistrationCSRFProtection(TestCase):
    def test_registration_without_csrf_token(self):
        status_code = form_without_csrf_token("registration", REGISTRATION_FORM_FIELDS)
        self.assertEqual(status_code, 403)

    def test_registration_with_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token(
            "registration", REGISTRATION_FORM_FIELDS
        )
        self.assertEqual(status_code, 403)

    def test_registration_with_valid_csrf_token(self):
        status_code = form_with_valid_csrf_token(
            "registration", REGISTRATION_FORM_FIELDS
        )
        self.assertEqual(status_code, 200)
