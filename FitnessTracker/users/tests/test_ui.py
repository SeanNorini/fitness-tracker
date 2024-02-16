import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import authenticate
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.models import User
from .test_globals import *
from common.selenium_utils import *
from common.test_utils import (
    form_without_csrf_token,
    form_with_invalid_csrf_token,
    form_with_valid_csrf_token,
)

from ..utils import account_token_generator


class SeleniumTestCase(StaticLiveServerTestCase):
    fixtures = ["default.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()


class TestLoginUI(SeleniumTestCase):
    def setUp(self) -> None:
        self.driver.get(self.live_server_url + "/user/login/")

    def test_elements_exist(self) -> None:
        elements = {"id": ["username", "password", "remember_me"], "name": ["login"]}
        assert elements_exist(self.driver, elements)

    def test_title(self) -> None:
        self.assertEqual(self.driver.title, "Fitness Tracker - Login")

    def test_links_exist(self) -> None:
        expected_links = [
            f"{self.live_server_url}/user/registration/",
            f"{self.live_server_url}/user/reset_password/",
        ]
        links = [
            link.get_attribute("href")
            for link in find_elements(self.driver, "tag", "a")
        ]

        self.assertListEqual(expected_links, links)

    def test_login_required_fields(self) -> None:
        required_fields = ["username", "password"]
        assert validate_required_fields(self.driver, "login_form", required_fields)


class TestRegistrationUI(SeleniumTestCase):
    def setUp(self) -> None:
        self.driver.get(self.live_server_url + "/user/registration/")

    def test_elements_exist(self) -> None:
        elements = {"name": REGISTRATION_FORM_FIELDS.keys()}
        self.assertTrue(elements_exist(self.driver, elements))

    def test_required_fields(self):
        required_fields = ["username", "password", "confirm_password", "email"]
        self.assertTrue(
            validate_required_fields(self.driver, "registration_form", required_fields)
        )

    def test_title(self) -> None:
        self.assertEqual(self.driver.title, "Fitness Tracker - Registration")

    def test_links_exist(self) -> None:
        expected_links = [
            f"{self.live_server_url}/user/login/",
        ]
        links = [
            link.get_attribute("href")
            for link in find_elements(self.driver, "tag", "a")
        ]

        self.assertListEqual(expected_links, links)


class TestActivateUI(SeleniumTestCase):
    def setUp(self) -> None:
        user = User.objects.get(username=USERNAME_VALID)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_token_generator.make_token(user)
        self.driver.get(
            self.live_server_url + reverse("activate", args=[uidb64, token])
        )

    def test_title(self) -> None:
        self.assertEqual(self.driver.title, "Fitness Tracker - Account Activation")

    def test_links_exist(self) -> None:
        expected_links = [
            f"{self.live_server_url}/workout/",
        ]
        links = [
            link.get_attribute("href")
            for link in find_elements(self.driver, "tag", "a")
        ]

        self.assertListEqual(expected_links, links)


class TestChangePasswordUI(SeleniumTestCase):
    def setUp(self) -> None:
        login(
            self.driver, self.live_server_url + "/user/login/", LOGIN_USER_FORM_FIELDS
        )
        self.driver.get(self.live_server_url + "/user/change_password/")

    def test_title(self) -> None:
        self.assertEqual(self.driver.title, "Fitness Tracker - Change Password")

    def test_links_exist(self) -> None:
        expected_links = [
            f"{self.live_server_url}/user/settings/",
        ]
        links = [
            link.get_attribute("href")
            for link in find_elements(self.driver, "tag", "a")
        ]

        self.assertListEqual(expected_links, links)

    def test_elements_exist(self) -> None:
        elements = {
            "name": [
                "current_password",
                "new_password",
                "confirm_password",
                "change_password",
            ]
        }
        self.assertTrue(elements_exist(self.driver, elements))

    def test_required_fields(self):
        required_fields = ["current_password", "new_password", "confirm_password"]
        self.assertTrue(
            validate_required_fields(
                self.driver, "change_password_form", required_fields
            )
        )


class TestResetPasswordUI(SeleniumTestCase):
    def setUp(self):
        self.driver.get(self.live_server_url + "/user/reset_password/")

    def test_title(self) -> None:
        self.assertEqual(self.driver.title, "Fitness Tracker - Reset Password")

    def test_links_exist(self) -> None:
        expected_links = [
            f"{self.live_server_url}/user/login/",
        ]
        links = [
            link.get_attribute("href")
            for link in find_elements(self.driver, "tag", "a")
        ]

        self.assertListEqual(expected_links, links)

    def test_elements_exist(self) -> None:
        elements = {"name": ["username"]}
        self.assertTrue(elements_exist(self.driver, elements))

    def test_required_fields(self):
        required_fields = ["username"]
        self.assertTrue(
            validate_required_fields(
                self.driver, "reset_password_form", required_fields
            )
        )

    def test_reset_password_failure(self) -> None:
        self.driver.get(
            self.live_server_url + "/user/reset_password/invalid_uid/invalid_token/"
        )
        header = find_element(self.driver, "id", "header")
        self.assertEqual(header.text, "Password Reset Error!")
        self.assertTrue(elements_exist(self.driver, {"name": ["return_to_site"]}))


class TestResetPasswordChangePasswordUI(SeleniumTestCase):
    def setUp(self) -> None:
        user = User.objects.get(username=USERNAME_VALID)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_token_generator.make_token(user)
        self.driver.get(
            self.live_server_url
            + reverse("reset_password_confirm_token", args=[uidb64, token])
        )

    def test_title(self) -> None:
        time.sleep(10)
        self.assertEqual(self.driver.title, "Fitness Tracker - Change Password")

    def test_links_exist(self) -> None:
        expected_links = [
            f"{self.live_server_url}/user/login/",
        ]
        links = [
            link.get_attribute("href")
            for link in find_elements(self.driver, "tag", "a")
        ]

        self.assertListEqual(expected_links, links)

    def test_elements_exist(self) -> None:
        elements = {"name": ["new_password", "confirm_password", "change_password"]}
        self.assertTrue(elements_exist(self.driver, elements))

    def test_required_fields(self):
        required_fields = ["new_password", "confirm_password"]
        self.assertTrue(
            validate_required_fields(
                self.driver, "change_password_form", required_fields
            )
        )
