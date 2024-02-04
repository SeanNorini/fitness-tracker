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

    def test_login_elements(self) -> None:
        self.driver.get(self.live_server_url + "/user/login")
        elements = {"id": ["username", "password", "remember_me"]}
        assert elements_exist(self.driver, elements)

    def test_login_successful(self) -> None:
        login(self.driver, self.live_server_url + "/user/login", LOGIN_USER_FORM_FIELDS)
        # greeting = find_element(self.driver, "id", "greeting")
        assert self.driver.current_url == self.live_server_url + "/"

    def test_login_validation(self) -> None:
        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": "test", "password": "invalid"},
        )

        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": "invalid", "password": "test"},
        )

        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": "test", "password": ""},
        )

        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": "", "password": "test"},
        )

        assert self.driver.current_url == (self.live_server_url + "/user/login/")

    def test_login_remember_me(self) -> None:
        pass
