from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from datetime import timedelta
from selenium import webdriver
import time
from log.models import CardioLog
from users.models import User
from common.test_globals import *
from common.selenium_utils import (
    click,
    login,
    find_element,
    drag_y,
)


class SeleniumTestCase(StaticLiveServerTestCase):
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


class TestCardio(SeleniumTestCase):
    def setUp(self) -> None:
        super().setUp()
        login(
            self.driver, self.live_server_url + "/user/login/", LOGIN_USER_FORM_FIELDS
        )
        time.sleep(5)
        self.driver.get(self.live_server_url + "/cardio")
        time.sleep(5)

    def test_summary_selection(self):
        click(self.driver, "id", "month")
        time.sleep(1)
        self.assertTrue("Current Month" in self.driver.page_source)

        click(self.driver, "id", "year")
        time.sleep(1)
        self.assertTrue("Current Year" in self.driver.page_source)

        click(self.driver, "id", "week")
        time.sleep(1)
        self.assertTrue("Current Day" in self.driver.page_source)

    def test_cardio_log_entry(self):
        # Click on form elements and let them expand before dragging inputs
        click(self.driver, "id", "date-header")
        click(self.driver, "id", "duration")
        click(self.driver, "id", "distance")
        time.sleep(3)

        element = find_element(self.driver, "id", "distance")
        self.driver.execute_script("""
        const viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
        const elementTop = arguments[0].getBoundingClientRect().top;
        window.scrollBy(0, elementTop-(viewPortHeight/2));
        """, element)

        drag_y(self.driver, "id", "date", 40)
        drag_y(self.driver, "id", "dur-hours", -20)
        drag_y(self.driver, "id", "dur-minutes", 20)
        drag_y(self.driver, "id", "dur-seconds", -20)
        drag_y(self.driver, "id", "dist-int", -40)
        drag_y(self.driver, "id", "dist-dec", -60)

        click(self.driver, "id", "save-cardio-session")

        time.sleep(1)
        popup = find_element(self.driver, "id", "popup-message")
        self.assertEqual(popup.text, "Cardio Session Saved.")

        log = CardioLog.objects.all().first()

        self.assertEqual(log.datetime.date(), timezone.now().date() - timedelta(days=2))
        self.assertEqual(log.duration.total_seconds(), 5341.0)
        self.assertEqual(log.distance, 2.02)
