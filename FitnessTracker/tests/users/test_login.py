import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.contrib.auth import authenticate
from users.models import User
from common.selenium_utils import *
from common.test_utils import (
    form_without_csrf_token,
    form_with_invalid_csrf_token,
    form_with_valid_csrf_token,
)
from django.urls import reverse

# Constants for login and registration form fields
LOGIN_USER_FORM_FIELDS = {"username": "testuser", "password": "testpassword"}


# Create your tests here.
class TestLoginUI(StaticLiveServerTestCase):
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
        self.driver.get(self.live_server_url + "/user/login")

    def test_login_elements_exist(self) -> None:
        elements = {"id": ["username", "password", "remember_me"]}
        assert elements_exist(self.driver, elements)

    def test_login_successful(self) -> None:
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        # greeting = find_element(self.driver, "id", "greeting")
        assert self.driver.current_url == self.live_server_url + "/"

    def test_login_unsuccessful(self) -> None:
        credentials = [
            {"username": "testuser", "password": "invalid"},
            {"username": "invalid", "password": "invalid"},
            {"username": "testuser", "password": ""},
            {"username": "", "password": "testpassword"},
        ]
        for user_login in credentials:
            fill_form(self.driver, user_login)
            click(self.driver, "name", "login")
            assert self.driver.current_url == (self.live_server_url + "/user/login/")
            clear_form(self.driver, user_login)

    def test_login_required_fields(self) -> None:
        required_fields = ["username", "password"]
        assert validate_required_fields(self.driver, "login_form", required_fields)

    def test_login_remember_me(self) -> None:
        # Click checkbox
        click(self.driver, "name", "remember_me")

        # Login User
        fill_form(self.driver, LOGIN_USER_FORM_FIELDS)
        click(self.driver, "name", "login")

        # Check that cookie won't expire on browser close
        assert get_cookie_expiration_time(self.driver, "sessionid") > 0

    def test_login_dont_remember_me(self) -> None:
        # Login User
        fill_form(self.driver, LOGIN_USER_FORM_FIELDS)
        click(self.driver, "name", "login")

        # Check that cookie expires on browser close
        assert get_cookie_expiration_time(self.driver, "sessionid") == 0

    def test_logout(self) -> None:
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        click(self.driver, "id", "logout")
        assert self.driver.current_url == (self.live_server_url + "/user/login/")


class TestLoginAuthentication(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_empty_username_and_password(self):
        user = authenticate(username="", password="")
        self.assertIsNone(user)

    def test_empty_username_non_empty_password(self):
        user = authenticate(username="", password="testpassword")
        self.assertIsNone(user)

    def test_non_empty_username_empty_password(self):
        user = authenticate(username="testuser", password="")
        self.assertIsNone(user)

    def test_valid_username_and_password(self):
        user = authenticate(username="testuser", password="testpassword")
        self.assertEqual(user, self.test_user)

    def test_invalid_username_non_empty_password(self):
        user = authenticate(username="invaliduser", password="testpassword")
        self.assertIsNone(user)

    def test_valid_username_invalid_password(self):
        user = authenticate(username="testuser", password="invalidpassword")
        self.assertIsNone(user)

    def test_invalid_username_empty_password(self):
        user = authenticate(username="invaliduser", password="")
        self.assertIsNone(user)


class TestLoginCSRFProtection(TestCase):
    def test_login_without_csrf_token(self):
        status_code = form_without_csrf_token("login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(status_code, 403)

    def test_login_with_invalid_csrf_token(self):
        status_code = form_with_invalid_csrf_token("login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(status_code, 403)

    def test_login_with_valid_csrf_token(self):
        status_code = form_with_valid_csrf_token("login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(status_code, 200)


def get_cookie_expiration_time(driver, cookie_name):
    """
    Gets the expiration time of a specific cookie.

    Args:
        driver: The Chrome WebDriver instance.
        cookie_name (str): The name of the cookie.

    Returns:
        int: The expiration time of the cookie.
    """
    # Get all cookies
    cookies = driver.get_cookies()

    # Find the specific cookie by name
    target_cookie = next(
        (cookie for cookie in cookies if cookie["name"] == cookie_name), None
    )

    # Extract and return the expiration time of the cookie
    if target_cookie:
        if "expiry" in target_cookie:
            return target_cookie["expiry"]

    return 0
