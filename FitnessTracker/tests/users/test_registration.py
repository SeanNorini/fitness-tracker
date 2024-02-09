import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from selenium import webdriver
from selenium.webdriver.common.by import By
from common.users_utils import *
from common.selenium_utils import validate_required_fields


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
        self.driver.get(self.live_server_url + "/user/registration")

    def register_user(self):
        self.driver.find_element(By.NAME, "username").send_keys("test_name")
        self.driver.find_element(By.NAME, "first_name").send_keys("first_name")
        self.driver.find_element(By.NAME, "last_name").send_keys("last_name")
        self.driver.find_element(By.NAME, "password").send_keys("test_pass")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("test_pass")
        self.driver.find_element(By.NAME, "email").send_keys("test@gmail.com")
        self.driver.find_element(By.NAME, "weight").send_keys("150")
        self.driver.find_element(By.NAME, "height").send_keys("75")
        self.driver.find_element(By.NAME, "age").send_keys("28")
        self.driver.find_element(By.NAME, "register").click()
        time.sleep(1)

    def test_registration_create_user(self):
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

    def test_registration_required_fields(self):
        required_fields = ["username", "password", "confirm_password", "email"]
        assert validate_required_fields(
            self.driver, "registration_form", required_fields
        )
