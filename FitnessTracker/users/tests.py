from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from selenium import webdriver
from .utilities import *
import time

# Constants for login and registration form fields
LOGIN_USER_FORM_FIELDS = {"username": "test", "password": "test"}


# Create your tests here.
class TestUsersSelenium(StaticLiveServerTestCase):
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

    def register_user(self):
        self.driver.get(f"{self.live_server_url}/user/registration")
        self.driver.find_element(By.NAME, "username").send_keys("test_name")
        self.driver.find_element(By.NAME, "first_name").send_keys("first_name")
        self.driver.find_element(By.NAME, "last_name").send_keys("last_name")
        self.driver.find_element(By.NAME, "password").send_keys("test_pass")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("test_pass")
        self.driver.find_element(By.NAME, "email").send_keys("snorini@gmail.com")
        self.driver.find_element(By.NAME, "weight").send_keys("150")
        self.driver.find_element(By.NAME, "height").send_keys("75")
        self.driver.find_element(By.NAME, "age").send_keys("28")
        self.driver.find_element(By.NAME, "register").click()
        time.sleep(1)

    def test_login_elements(self) -> None:
        elements = {"id": ["username", "password", "remember_me"]}
        assert elements_exist(self.driver, elements)

    def test_login_successful(self) -> None:
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        # greeting = find_element(self.driver, "id", "greeting")
        assert self.driver.current_url == self.live_server_url + "/"

    def test_login_validation(self) -> None:
        credentials = [
            {"username": "test", "password": "invalid"},
            {"username": "invalid", "password": "test"},
            {"username": "test", "password": ""},
            {"username": "", "password": "test"},
        ]
        for user_login in credentials:
            fill_form(self.driver, user_login)
            assert self.driver.current_url == (self.live_server_url + "/user/login/")
            clear_form(self.driver, user_login)

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

    def test_registration(self):
        # Confirm user does not exist
        try:
            User.objects.get(username="test_name")
            raise IntegrityError
        except ObjectDoesNotExist:
            pass
        # Create user
        self.register_user()

        # Confirm user created
        assert User.objects.get(username="test_name")
