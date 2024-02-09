from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from common.selenium_utils import *
import time

LOGIN_USER_FORM_FIELDS = {"username": "test", "password": "test"}


# Create your tests here.
class TestWorkoutSelenium(StaticLiveServerTestCase):
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
        login(
            self.driver, (self.live_server_url + "/user/login"), LOGIN_USER_FORM_FIELDS
        )

    def test_save_workout(self):
        click(self.driver, "class", "edit_workouts")

        click(self.driver, "class", "exit_edit")
