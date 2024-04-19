from datetime import date
from unittest.mock import MagicMock
from django.test import TestCase
from log.utils import Calendar


class TestCalendar(TestCase):
    def setUp(self):
        # Mock logs
        self.workout_logs = MagicMock()
        self.weight_logs = MagicMock()
        self.cardio_logs = MagicMock()

        # Create instances of the calendar
        self.calendar = Calendar(
            firstweekday=6,
            workout_logs=self.workout_logs,
            weight_logs=self.weight_logs,
            cardio_logs=self.cardio_logs,
        )

    def test_formatday_with_logs(self):
        # Setup the logs to return a log object on specific days
        self.workout_logs.filter.return_value.first.return_value = MagicMock(
            date=date(2022, 4, 15)
        )
        self.weight_logs.filter.return_value.first.return_value = None
        self.cardio_logs.filter.return_value.first.return_value = MagicMock(
            datetime=date(2022, 4, 15)
        )

        # Day with workout and cardio log
        result = self.calendar.formatday(15, 5)
        self.assertIn("exercise-icon", result)
        self.assertIn("steps-icon", result)
        self.assertNotIn("monitor_weight-icon", result)

    def test_formatday_without_logs(self):
        # Setup logs to return None (no logs on that day)
        self.workout_logs.filter.return_value.first.return_value = None
        self.weight_logs.filter.return_value.first.return_value = None
        self.cardio_logs.filter.return_value.first.return_value = None

        # Day without any logs
        result = self.calendar.formatday(10, 3)
        self.assertNotIn("exercise-icon", result)
        self.assertNotIn("monitor_weight-icon", result)
        self.assertNotIn("steps-icon", result)

    def test_formatmonth(self):
        result = self.calendar.formatmonth(2022, 4)
        self.assertIn("navigate_before", result)
        self.assertIn("navigate_next", result)
        self.assertIn("month p-0_2", result)
