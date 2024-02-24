import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import authenticate
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
)
from seleniumlogin import force_login


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

    def setUp(self) -> None:
        self.user = User.objects.create_user(**CREATE_USER)
        force_login(self.user, self.driver, self.live_server_url)
        self.driver.get(self.live_server_url + "/workouts")


class TestWorkoutUI(SeleniumTestCase):

    def test_elements_exist(self) -> None:
        elements = {
            "id": [
                "date",
                "select_workout",
                "select_exercise",
                "workout_tooltip",
                "save_workout_session",
                "add_exercise",
            ],
        }
        assert elements_exist(self.driver, elements)

    def test_title(self) -> None:
        self.assertEqual(self.driver.title, "Fitness Tracker - Workout")
