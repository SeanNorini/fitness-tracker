import datetime
import time
from selenium.webdriver.support.ui import WebDriverWait
from log.models import WorkoutLog
from workout.models import Workout, WorkoutSettings
from selenium.webdriver.common.action_chains import ActionChains
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from users.models import User
from common.test_globals import CREATE_USER
from common.selenium_utils import (
    login,
    click,
    find_element,
    find_elements,
    wait_until_visible,
    set_date,
)
from django.core import management


class WorkoutTestCase(StaticLiveServerTestCase):
    fixtures = ["test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.driver = webdriver.Chrome()
        cls.user = User.objects.create_user(**CREATE_USER)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.default_user = User.objects.get(username="default")
        login(
            self.driver,
            self.live_server_url + "/user/login",
            {"username": "default", "password": "demouser"},
        )
        self.driver.get(self.live_server_url + "/workout/")
        self.driver.implicitly_wait(5)
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def select_from_search_list(self, search_bar_id, options_id, text):
        """
        Opens a search list, selects an item based on the text, and verifies if it disappears after selection.

        Args:
        search_bar_id (str): The ID of the element to click to open the search list.
        options_id (str): The ID of the search list element.
        text (str): The text of the item to select within the search list.
        """
        click(self.driver, "id", search_bar_id)
        search_list = wait_until_visible(self.driver, "id", options_id)
        click(search_list, "xpath", f"//div[contains(text(), '{text}')]")
        return not search_list.is_displayed()


class TestWorkout(WorkoutTestCase):

    def test_select_exercise(self):
        """Verifies that user is able to click on exercise list, select an exercise, and the exercise is
        added to the workout and the search list closes."""
        search_bar = wait_until_visible(self.driver, "id", "add-exercise")
        result = self.select_from_search_list(
            "add-exercise", "add-exercise-options", "Bench Press"
        )
        exercises = find_elements(self.driver, "class", "exercise-name")

        self.assertTrue(result)
        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0].text, "Bench Press")

    def test_select_workout(self):
        """Verifies that user can select a workout and the populated exercises match expected values"""
        search_bar = wait_until_visible(self.driver, "id", "select-workout")
        result = self.select_from_search_list(
            "select-workout", "select-workout-options", "Starting Strength - A"
        )
        exercises = find_elements(self.driver, "class", "exercise-name")

        self.assertTrue(result)
        self.assertEqual(len(exercises), 3)
        self.assertEqual(exercises[0].text, "Back Squat")
        self.assertEqual(exercises[1].text, "Bench Press")
        self.assertEqual(exercises[2].text, "Deadlift")

    def test_save_workout(self):
        """Verifies that user can save a workout, proper notification is displayed,
        and workout log is created with expected values"""
        self.select_from_search_list(
            "select-workout", "select-workout-options", "Starting Strength - A"
        )
        time.sleep(1)
        click(self.driver, "id", "save-workout")
        time.sleep(1)
        popup = find_element(self.driver, "id", "popup-message")
        self.assertEqual(popup.text, "Workout Saved")
        workout_log = (
            WorkoutLog.objects.filter(user=self.default_user).order_by("-date").first()
        ).generate_workout_log()

        self.assertEqual(workout_log["workout_name"], "Starting Strength - A")
        self.assertEqual(len(workout_log["exercises"]), 3)
        self.assertEqual(workout_log["exercises"][0]["name"], "Back Squat")
        self.assertEqual(workout_log["exercises"][1]["name"], "Bench Press")
        self.assertEqual(workout_log["exercises"][2]["name"], "Deadlift")

    def test_select_date(self):
        """Verifies date selection starts on current day and only allows previous dates for input"""
        # Verify date starts at current day
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        date_input = find_element(self.driver, "id", "date")
        self.assertEqual(date_input.get_attribute("value"), current_date)

        # Verify cannot set future date
        date_input.click()  # Focus on the element
        set_date(self.driver, "date", "9999-01-01")
        date_input.send_keys(Keys.DOWN)
        popup = find_element(self.driver, "id", "popup-message")
        self.assertEqual(popup.text, "Cannot set day to a future date.")
        self.assertEqual(date_input.get_attribute("value"), current_date)

        # Verify can set past date
        date_input.click()
        set_date(self.driver, "date", "2024-01-01")
        date_input.send_keys(Keys.DOWN)
        self.assertEqual(date_input.get_attribute("value"), "2023-01-01")

    def test_drag_and_drop(self):
        """Verifies that exercise elements within a workout can be drag and dropped into a new position, and
        that positioning functions correctly"""
        self.select_from_search_list(
            "select-workout", "select-workout-options", "Starting Strength - A"
        )
        exercises = find_elements(self.driver, "class", "exercise-name")
        ActionChains(self.driver).click_and_hold(exercises[2]).move_to_element(
            exercises[0]
        ).release().perform()

        exercises = find_elements(self.driver, "class", "exercise-name")
        self.assertEqual(len(exercises), 3)
        self.assertEqual(exercises[0].text, "Deadlift")
        self.assertEqual(exercises[1].text, "Back Squat")
        self.assertEqual(exercises[2].text, "Bench Press")

    def test_workout_timer(self):
        """Verify start and stop on timer, as well as accurate time keeping"""
        workout_settings = WorkoutSettings.objects.get(user=self.default_user)
        workout_settings.show_workout_timer = True
        workout_settings.save()

        self.driver.refresh()
        timer_control = find_element(self.driver, "class", "timer-control")
        timer_display = find_element(self.driver, "id", "workout-timer")
        self.assertEqual(timer_display.text, "00:00:00")

        for _ in range(2):
            timer_control.click()
            time.sleep(2)
            self.assertEqual(timer_display.text, "00:00:02")

        click(self.driver, "class", "timer-reset-control")
        self.driver.switch_to.alert.accept()
        self.assertEqual(timer_display.text, "00:00:00")

        for _ in range(20):
            timer_control.click()
        self.assertEqual(timer_display.text, "00:00:00")

    def test_delete_exercise(self):
        self.select_from_search_list(
            "add-exercise", "add-exercise-options", "Bench Press"
        )
        click(self.driver, "class", "delete-exercise")
        exercise = find_element(self.driver, "class", "exercise")
        self.assertFalse(exercise)

    def test_add_and_delete_exercise_set(self):
        self.select_from_search_list(
            "add-exercise", "add-exercise-options", "Bench Press"
        )
        for _ in range(4):
            click(self.driver, "class", "add-set")
        exercise_sets = find_elements(self.driver, "class", "set")
        self.assertEqual(len(exercise_sets), 5)

        for _ in range(3):
            click(self.driver, "class", "delete-set")
        exercise_sets = find_elements(self.driver, "class", "set")
        self.assertEqual(len(exercise_sets), 2)

    def test_rest_timer(self):
        workout_settings = WorkoutSettings.objects.get(user=self.default_user)
        workout_settings.show_rest_timer = True
        workout_settings.save()
        self.driver.refresh()

        self.select_from_search_list(
            "add-exercise", "add-exercise-options", "Bench Press"
        )
        click(self.driver, "class", "toggleButton")
        rest_timer = wait_until_visible(self.driver, "id", "rest-timer")
        self.assertTrue(rest_timer.is_displayed())
        time.sleep(3)
        rest_timer_display = find_element(self.driver, "id", "rest-timer-display")
        self.assertEqual(rest_timer_display.text, "00:03")



class TestExerciseSettings(WorkoutTestCase):
    pass


class TestWorkoutSettings(WorkoutTestCase):
    pass


class TestRoutineSettings(WorkoutTestCase):
    pass
