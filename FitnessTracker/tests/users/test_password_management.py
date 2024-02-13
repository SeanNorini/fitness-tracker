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


LOGIN_USER_FORM_FIELDS = {"username": "test_name", "password": "testpassword"}
CHANGE_PASSWORD_FORM_FIELDS = {
    "current_password": LOGIN_USER_FORM_FIELDS["password"],
    "new_password": "test_pass123",
    "confirm_password": "test_pass123",
}


class TestChangePasswordUI(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self) -> None:
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
            is_active=True,
        )
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        self.driver.get(self.live_server_url + "/user/change_password/")

    def test_password_change_successful(self):
        fill_form(self.driver, CHANGE_PASSWORD_FORM_FIELDS)
        click(self.driver, "name", "change_password")

        # check for validation
        header = find_element(self.driver, "tag", "h1")
        self.assertEqual(header.text, "Password Changed!")

        click(self.driver, "name", "return_to_settings")
        self.assertEqual(
            self.driver.current_url, self.live_server_url + "/user/settings/"
        )

    def test_change_password_elements_exist(self) -> None:
        elements = {"id": ["current_password", "new_password", "confirm_password"]}
        assert elements_exist(self.driver, elements)


class TestChangePasswordCSRFProtection(TestCase):
    def test_change_password_without_csrf_token(self):
        status_code = form_without_csrf_token(
            "registration", CHANGE_PASSWORD_FORM_FIELDS
        )
        self.assertEqual(status_code, 403)

    def test_change_password_with_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token(
            "registration", CHANGE_PASSWORD_FORM_FIELDS
        )
        self.assertEqual(status_code, 403)

    def test_change_password_with_valid_csrf_token(self):
        status_code = form_with_valid_csrf_token(
            "registration", CHANGE_PASSWORD_FORM_FIELDS
        )
        self.assertEqual(status_code, 200)
