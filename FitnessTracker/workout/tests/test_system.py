from common.test_utils import SeleniumTestCase


class TestWorkout(SeleniumTestCase):
    def test_select_exercise(self):
        # Shows select exercise
        # Exercise is correct
        pass

    def test_select_workout(self):
        # Shows selected workout
        # Workout is correct
        pass

    def test_save_workout(self):
        # Save workout populates correctly model
        # Can't save with no exercises
        # Show popup on save
        pass

    def test_select_date(self):
        # Can select date
        # Can't select future date (shows popup)
        pass

    def test_drag_and_drop(self):
        # Swap two exercises with drag and hold, check if positions changed on dom
        pass


class TestExerciseSettings(SeleniumTestCase):
    pass


class TestWorkoutSettings(SeleniumTestCase):
    pass


class TestRoutineSettings(SeleniumTestCase):
    pass
