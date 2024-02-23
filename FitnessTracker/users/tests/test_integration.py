import time
from unittest.mock import patch

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import IntegrityError
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.models import User
from common.test_globals import *
from common.selenium_utils import *
from common.test_utils import (
    form_without_csrf_token,
    form_with_invalid_csrf_token,
    form_with_valid_csrf_token,
    get_cookie_expiration_time,
)

from users.forms import RegistrationForm
from ..utils import account_token_generator


class SeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()


class TestLogin(SeleniumTestCase):
    fixtures = ["default.json"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(**CREATE_USER)
        self.driver.get(self.live_server_url + "/user/login")

    def test_login_successful_with_email(self) -> None:
        # Verify login with valid email and password
        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": EMAIL_VALID, "password": PASSWORD_VALID},
        )
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workouts/")

    def test_login_successful_with_username(self) -> None:
        # Verify login with valid username and password
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workouts/")

    def test_login_unsuccessful(self) -> None:
        # Verify user can't login with incorrect credentials
        credentials = [
            {"username": USERNAME_VALID, "password": PASSWORD_INVALID},
            {"username": USERNAME_INVALID, "password": PASSWORD_INVALID},
        ]
        # Attempt login with invalid credentials
        for user_login in credentials:
            fill_form(self.driver, user_login)
            click(self.driver, "name", "login")

            # Verify user is still on login page and errors are showing
            self.assertEqual(
                self.driver.current_url, self.live_server_url + "/user/login/"
            )
            self.assertTrue(elements_exist(self.driver, {"class": ["errorlist"]}))

            # Clear form for next input
            clear_form(self.driver, user_login)

    def test_remember_me(self) -> None:
        # Click checkbox
        click(self.driver, "name", "remember_me")
        # Login User
        fill_form(self.driver, LOGIN_USER_FORM_FIELDS)
        click(self.driver, "name", "login")

        # Check that cookie won't expire on browser close

        self.assertTrue(get_cookie_expiration_time(self.driver, "sessionid") > 0)

    def test_dont_remember_me(self) -> None:
        # Login User
        fill_form(self.driver, LOGIN_USER_FORM_FIELDS)
        click(self.driver, "name", "login")

        # Check that cookie expires on browser close
        self.assertTrue(get_cookie_expiration_time(self.driver, "sessionid") == 0)

    def test_link_to_registration(self) -> None:
        click(self.driver, "id", "registration")
        self.assertEqual(
            self.driver.current_url, self.live_server_url + "/user/registration/"
        )

    def test_link_to_account_recovery(self) -> None:
        click(self.driver, "id", "reset_password")
        self.assertEqual(
            self.driver.current_url, self.live_server_url + "/user/reset_password/"
        )


class TestLogout(SeleniumTestCase):
    fixtures = ["default.json"]

    def test_logout(self) -> None:
        user = User.objects.create_user(**CREATE_USER)
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        click(self.driver, "id", "logout")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")


class TestRegistration(SeleniumTestCase):
    fixtures = ["default.json"]

    def setUp(self) -> None:
        self.driver.get(self.live_server_url + "/user/registration/")

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
                f"Thank you for registering, {REGISTRATION_FORM_FIELDS['username']}!",
            )

    def test_registration_unsuccessful(self):
        user = RegistrationForm(REGISTRATION_FORM_FIELDS).save()
        self.assertTrue(User.objects.get(username=REGISTRATION_FORM_FIELDS["username"]))

        with patch("users.views.send_activation_link") as send_activation_link:
            fill_form(self.driver, REGISTRATION_FORM_FIELDS)
            click(self.driver, "name", "register")
            time.sleep(1)  # Delay for server to process form
            self.assertTrue(elements_exist(self.driver, {"class": ["errorlist"]}))

    def test_link_to_login(self) -> None:
        click(self.driver, "id", "login")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")


class TestActivate(SeleniumTestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.activation_url = self.live_server_url + reverse(
            "activate", args=[uidb64, token]
        )
        self.driver.get(self.activation_url)

    def test_link_to_index(self):
        click(self.driver, "name", "return_to_site")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/")

    def test_redirect(self):
        time.sleep(4)
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workouts/")


class TestChangePassword(SeleniumTestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        self.driver.get(self.live_server_url + "/user/change_password/")

    def test_change_password_success(self) -> None:
        fill_form(self.driver, CHANGE_PASSWORD_FORM_FIELDS)
        click(self.driver, "name", "change_password")
        header = find_element(self.driver, "tag", "h1")
        self.assertEqual(header.text, "Password Changed!")
        click(self.driver, "name", "return_to_settings")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/settings")

    def test_change_password_fail(self) -> None:
        fill_form(
            self.driver,
            {
                "current_password": PASSWORD_INVALID,
                "new_password": PASSWORD_INVALID,
                "confirm_password": PASSWORD_INVALID,
            },
        )
        click(self.driver, "name", "change_password")
        self.assertTrue(elements_exist(self.driver, {"class": ["errorlist"]}))
