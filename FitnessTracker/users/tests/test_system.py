from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db import IntegrityError
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from selenium import webdriver
from unittest.mock import patch
import time
from users.models import User
from common.test_globals import *
from common.selenium_utils import (
    get_value,
    fill_form,
    click,
    login,
    clear_form,
    is_selected,
    elements_exist,
    find_element,
)
from common.test_utils import (
    get_cookie_expiration_time,
)

from users.forms import RegistrationForm
from users.services import account_token_generator


class SeleniumTestCase(StaticLiveServerTestCase):
    driver = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.user = User.objects.create_user(**CREATE_USER)


class TestLogin(SeleniumTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.driver.get(self.live_server_url + "/user/login")

    def test_login_successful_with_email(self) -> None:
        # Verify login with valid email and password
        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": EMAIL_VALID, "password": PASSWORD_VALID},
        )
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workout")

    def test_login_successful_with_username(self) -> None:
        # Verify login with valid username and password
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workout")

    def test_login_unsuccessful(self) -> None:
        # Verify user can't log in with incorrect credentials
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
        click(self.driver, "id", "reset-password")
        self.assertEqual(
            self.driver.current_url, self.live_server_url + "/user/reset_password/"
        )


class TestLogout(SeleniumTestCase):

    def test_logout(self) -> None:
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        click(self.driver, "id", "logout")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")


class TestRegistration(SeleniumTestCase):

    def setUp(self) -> None:
        self.driver.get(self.live_server_url + "/user/registration/")

    def test_registration_successful(self):
        # Confirm user does not exist
        if len(User.objects.filter(username=REGISTRATION_FORM_FIELDS["username"])) > 0:
            raise IntegrityError

        with patch(
            "users.services.EmailService.send_activation_link"
        ) as send_activation_link:
            fill_form(self.driver, REGISTRATION_FORM_FIELDS)
            click(self.driver, "name", "register")
            time.sleep(1)
            assert User.objects.get(username=REGISTRATION_FORM_FIELDS["username"])
            form_header = find_element(
                self.driver, "id", "registration-confirmation-header"
            ).text
            self.assertEqual(
                form_header,
                f"Thank you for registering, {REGISTRATION_FORM_FIELDS['username']}!",
            )

    def test_registration_unsuccessful(self):
        RegistrationForm(REGISTRATION_FORM_FIELDS).save()
        self.assertTrue(User.objects.get(username=REGISTRATION_FORM_FIELDS["username"]))

        with patch(
            "users.services.EmailService.send_activation_link"
        ) as send_activation_link:
            fill_form(self.driver, REGISTRATION_FORM_FIELDS)
            click(self.driver, "name", "register")
            time.sleep(1)  # Delay for server to process form
            self.assertTrue(elements_exist(self.driver, {"class": ["errorlist"]}))

    def test_link_to_login(self) -> None:
        click(self.driver, "id", "login")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")


class TestActivate(SeleniumTestCase):

    def setUp(self):
        super().setUp()
        self.user.is_active = False
        self.user.save()
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.activation_url = self.live_server_url + reverse(
            "activate", args=[uidb64, token]
        )
        self.driver.get(self.activation_url)

    def test_link_to_index(self):
        click(self.driver, "name", "return_to_site")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workout")

    def test_redirect(self):
        time.sleep(6)
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workout")


class TestChangePassword(SeleniumTestCase):

    def setUp(self):
        super().setUp()
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        self.driver.get(self.live_server_url + "/user/settings/")
        time.sleep(1)
        click(self.driver, "id", "change-password")

    def test_change_password_success(self) -> None:
        time.sleep(1)
        fill_form(self.driver, CHANGE_PASSWORD_FORM_FIELDS)
        click(self.driver, "id", "change-password")

        time.sleep(1)
        popup_message = find_element(self.driver, "id", "popup-message")
        self.assertEqual(popup_message.text, "Password Updated.")
        self.assertTrue(find_element(self.driver, "id", "account-settings-form"))

    def test_change_password_fail(self) -> None:
        time.sleep(1)
        fill_form(
            self.driver,
            {
                "current_password": PASSWORD_INVALID,
                "new_password": PASSWORD_INVALID,
                "confirm_password": PASSWORD_INVALID,
            },
        )
        click(self.driver, "id", "change-password")
        time.sleep(1)
        self.assertTrue(elements_exist(self.driver, {"class": ["errors"]}))

    def test_return_to_settings_btn(self) -> None:
        time.sleep(1)
        click(self.driver, "id", "return-to-settings")
        time.sleep(1)
        self.assertTrue(find_element(self.driver, "id", "account-settings-form"))


class TestResetPassword(SeleniumTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.driver.get(self.live_server_url + "/user/reset_password/")

    def test_reset_password(self) -> None:
        fill_form(self.driver, {"username": USERNAME_VALID})
        click(self.driver, "id", "reset-password")
        self.assertEqual(
            self.driver.current_url, self.live_server_url + "/user/reset_password/"
        )
        self.assertEqual(self.driver.title, "Fitness Tracker - Password Reset")
        click(self.driver, "id", "return-to-login")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")
        self.assertEqual(self.driver.title, "Fitness Tracker - Login")

    def test_return_to_login(self):
        click(self.driver, "id", "return-to-login")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")
        self.assertEqual(self.driver.title, "Fitness Tracker - Login")

    def test_reset_password_success(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.driver.get(
            self.live_server_url + f"/user/reset_password/{uidb64}/{token}/"
        )
        fill_form(
            self.driver,
            {"new_password": "new_password", "confirm_password": "new_password"},
        )
        click(self.driver, "name", "change-password")
        click(self.driver, "id", "return-to-site")
        self.assertEqual(self.driver.current_url, self.live_server_url + "/workout")

    def test_reset_password_failure(self) -> None:
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_token_generator.make_token(self.user)
        self.driver.get(
            self.live_server_url + f"/user/reset_password/{uidb64}/{token}/"
        )
        fill_form(
            self.driver,
            {"new_password": "new_password", "confirm_password": "invalid_password"},
        )
        click(self.driver, "name", "change-password")
        self.assertTrue(elements_exist(self.driver, {"class": ["errorlist"]}))


class TestSettings(SeleniumTestCase):
    def setUp(self):
        super().setUp()
        login(
            self.driver, self.live_server_url + "/user/login/", LOGIN_USER_FORM_FIELDS
        )
        self.driver.get(self.live_server_url + "/user/settings/")

    def test_update_full_account(self):
        account_data = {
            "first_name": "newfirstname",
            "last_name": "newlastname",
            "email": "new_email@gmail.com",
            "confirm_email": "new_email@gmail.com",
        }
        clear_form(self.driver, account_data)
        fill_form(self.driver, account_data)
        click(self.driver, "id", "update-account")
        self.driver.get(self.live_server_url + "/user/settings/")
        time.sleep(1)
        first_name = get_value(self.driver, "name", "first_name")
        last_name = get_value(self.driver, "name", "last_name")
        email = get_value(self.driver, "name", "email")
        self.assertEqual(first_name, "newfirstname")
        self.assertEqual(last_name, "newlastname")
        self.assertEqual(email, "new_email@gmail.com")

    def test_update_partial_account(self):
        clear_form(self.driver, {"first_name": "newfirstname"})
        fill_form(self.driver, {"first_name": "newfirstname"})
        click(self.driver, "id", "update-account")
        self.driver.get(self.live_server_url + "/user/settings/")
        time.sleep(1)
        first_name = get_value(self.driver, "name", "first_name")
        last_name = get_value(self.driver, "name", "last_name")
        self.assertEqual(first_name, "newfirstname")
        self.assertEqual(last_name, "last")

    def test_update_full_user_settings(self):
        user_settings_data = {
            "age": 35,
            "height": 75,
            "body_weight": 200,
            "body_fat": 25,
        }
        clear_form(self.driver, user_settings_data)
        fill_form(self.driver, user_settings_data)
        click(self.driver, "id", "system_of_measurement_1")
        click(self.driver, "id", "gender_1")
        click(self.driver, "id", "update-user-settings")
        self.driver.get(self.live_server_url + "/user/settings/")
        time.sleep(1)
        age = get_value(self.driver, "name", "age")
        height = get_value(self.driver, "name", "height")
        body_weight = get_value(self.driver, "name", "body_weight")
        body_fat = get_value(self.driver, "name", "body_fat")
        self.assertEqual(age, "35")
        self.assertEqual(height, "75.0")
        self.assertEqual(body_weight, "200.0")
        self.assertEqual(body_fat, "25.0")
        self.assertTrue(is_selected(self.driver, "id", "gender_1"))
        self.assertTrue(is_selected(self.driver, "id", "system_of_measurement_1"))

    def test_update_partial_user_settings(self):
        user_settings_data = {
            "body_weight": 200,
            "body_fat": 25,
        }
        clear_form(self.driver, user_settings_data)
        fill_form(self.driver, user_settings_data)
        click(self.driver, "id", "update-user-settings")
        self.driver.get(self.live_server_url + "/user/settings/")
        time.sleep(1)
        body_weight = get_value(self.driver, "name", "body_weight")
        body_fat = get_value(self.driver, "name", "body_fat")
        self.assertEqual(body_weight, "200.0")
        self.assertEqual(body_fat, "25.0")

    def test_delete_account(self):
        time.sleep(1)
        click(self.driver, "id", "delete-account")
        confirmation = self.driver.switch_to.alert
        confirmation.send_keys("delete")
        confirmation.accept()
        time.sleep(1)
        # Verify redirect after account deletion
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")
        login(
            self.driver, self.live_server_url + "/user/login/", LOGIN_USER_FORM_FIELDS
        )
        # Verify user doesn't exist
        self.assertEqual(self.driver.current_url, self.live_server_url + "/user/login/")
        self.assertTrue(find_element(self.driver, "class", "errorlist"))
