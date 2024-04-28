import time
from common.test_utils import SeleniumTestCase
from common.selenium_utils import find_element, click, login, find_elements
from selenium.webdriver.common.by import By
from users.models import User
from log.models import WeightLog, WorkoutLog
from datetime import datetime

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def month_number(month_name):
    return MONTHS.get(month_name, None)


class TestLogView(SeleniumTestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        super().setUp()
        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": "default", "password": "demouser"},
        )
        self.driver.get(self.live_server_url + "/log")
        self.driver.implicitly_wait(5)

    def test_navigate_calendar(self):
        """Verify calendar navigation works"""
        self.driver.get(self.live_server_url + "/log/2024/4")

        with self.subTest("Loads correct starting date"):
            month, year = find_element(self.driver, "id", "month-name").text.split(" ")
            self.assertEqual(month_number(month), 4)
            self.assertEqual(year, "2024")

        with self.subTest("Navigate previous returns correct month"):
            click(self.driver, "id", "nav-prev")
            time.sleep(1)
            month, year = find_element(self.driver, "id", "month-name").text.split(" ")
            self.assertEqual(month_number(month), 3)
            self.assertEqual(year, "2024")

        with self.subTest("Navigate next returns correct month"):
            click(self.driver, "id", "nav-next")
            time.sleep(1)
            month, year = find_element(self.driver, "id", "month-name").text.split(" ")
            self.assertEqual(month_number(month), 4)
            self.assertEqual(year, "2024")

        with self.subTest("Rollover end of last year"):
            self.driver.get(self.live_server_url + "/log/2024/1")
            click(self.driver, "id", "nav-prev")
            time.sleep(1)
            month, year = find_element(self.driver, "id", "month-name").text.split(" ")
            self.assertEqual(month_number(month), 12)
            self.assertEqual(year, "2023")

        with self.subTest("Rollover beginning of next year"):
            self.driver.get(self.live_server_url + "/log/2024/12")
            click(self.driver, "id", "nav-next")
            time.sleep(1)
            month, year = find_element(self.driver, "id", "month-name").text.split(" ")
            self.assertEqual(month_number(month), 1)
            self.assertEqual(year, "2025")

    def test_get_log(self):
        """Pulls up a daily log and verifies all logs. Should verify a weight log,
        a single workout, and a single cardio session"""
        self.driver.get(self.live_server_url + "/log/2024/4")
        time.sleep(1)
        element = self.driver.find_element(By.CSS_SELECTOR, '[data-day="16"]')
        element.click()

        with self.subTest("Verify weight log"):
            time.sleep(1)
            body_weight = find_element(self.driver, "class", "body-weight").text.strip()
            body_fat = find_element(self.driver, "class", "body-fat").text.strip()
            self.assertEqual(body_weight, "Body Weight - 160.0 Lbs")
            self.assertEqual(body_fat, "Body Fat - 20.0%")

        with self.subTest("Verify workout log"):
            workout_name = find_elements(self.driver, "class", "workout-name")
            self.assertTrue(len(workout_name) == 1)
            self.assertEqual(workout_name[0].text.strip(), "Winter Warrior")

            workout_name[0].click()
            time.sleep(1)
            exercises = find_elements(self.driver, "class", "exercise-name")
            expected_exercises = ["Face Pull", "Power Clean", "Sumo Deadlift", "Plank"]
            for exercise in exercises:
                self.assertIn(exercise.text.strip(), expected_exercises)

        with self.subTest("Verify cardio log"):
            duration = find_element(self.driver, "class", "duration").text.strip()
            distance = find_element(self.driver, "class", "distance").text.strip()
            pace = find_element(self.driver, "class", "pace").text.strip()

            self.assertEqual(duration, "1h 30' 00\"")
            self.assertEqual(distance, "14.0")
            self.assertEqual(pace, "6' 25\"")

    def test_weight_log(self):
        """Tests user ability to create, edit and delete a weight log from the calendar"""
        time.sleep(1)
        element = self.driver.find_element(By.CSS_SELECTOR, '[data-day="1"]')
        element.click()

        with self.subTest("Verify weight log creation"):
            time.sleep(1)

            # Verify record doesn't exist
            placeholder = find_element(self.driver, "class", "weight-log-placeholder")
            self.assertEqual(placeholder.text.strip(), "No weight entry found.")

            find_element(self.driver, "class", "add-weight-log").click()
            time.sleep(1)

            click(self.driver, "id", "save-weight-log")

            body_weight = find_element(self.driver, "class", "body-weight").text.strip()
            body_fat = find_element(self.driver, "class", "body-fat").text.strip()
            self.assertEqual(body_weight, "Body Weight - 160.0 Lbs")
            self.assertEqual(body_fat, "Body Fat - 20.0%")

        with self.subTest("Verify weight log editing"):
            time.sleep(1)
            # Verify record exists
            body_weight = find_element(self.driver, "class", "body-weight").text.strip()
            self.assertEqual(body_weight, "Body Weight - 160.0 Lbs")

            find_element(self.driver, "class", "add-weight-log").click()
            time.sleep(1)
            body_weight_input = find_element(self.driver, "id", "body-weight")
            body_weight_input.clear()
            body_weight_input.send_keys("150")

            body_fat_input = find_element(self.driver, "id", "body-fat")
            body_fat_input.clear()
            body_fat_input.send_keys("15")

            click(self.driver, "id", "save-weight-log")

            body_weight = find_element(self.driver, "class", "body-weight").text.strip()
            body_fat = find_element(self.driver, "class", "body-fat").text.strip()
            self.assertEqual(body_weight, "Body Weight - 150 Lbs")
            self.assertEqual(body_fat, "Body Fat - 15%")

        with self.subTest("Verify weight log deletion"):
            # Verify record exists
            body_weight = find_element(self.driver, "class", "body-weight").text.strip()
            self.assertEqual(body_weight, "Body Weight - 150 Lbs")

            find_element(self.driver, "class", "delete-weight-log").click()
            placeholder = find_element(self.driver, "class", "weight-log-placeholder")
            self.assertEqual(placeholder.text.strip(), "No weight entry found.")
