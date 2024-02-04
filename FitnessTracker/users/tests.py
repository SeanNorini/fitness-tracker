from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
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
