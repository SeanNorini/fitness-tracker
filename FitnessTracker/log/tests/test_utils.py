from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock
from datetime import date

from log.models import WorkoutLog, CardioLog, WeightLog
from log.utils import Calendar
from users.models import User
from common.test_globals import CREATE_USER
from workout.models import Workout


class TestCalendar(TestCase):
    def setUp(self):
        self.user = User.objects.create(**CREATE_USER)
        self.year = timezone.now().year
        self.month = timezone.now().month
        # Create instances of the calendar
        self.calendar = Calendar(
            firstweekday=6,
            user=self.user,
            year=self.year,
            month=self.month,
        )
        self.workout = Workout.objects.create(user=self.user, name="Test Workout")
        self.workout_log = WorkoutLog.objects.create(
            user=self.user,
            workout=self.workout,
            date=timezone.datetime(self.year, self.month, 15),
            total_time=timezone.timedelta(minutes=30),
        )

        self.cardio_log = CardioLog.objects.create(
            user=self.user,
            datetime=timezone.datetime(self.year, self.month, 15, 10, 30),
            duration=timezone.timedelta(minutes=30),
            distance=5.0,
        )

        self.weight_log = WeightLog.objects.create(
            user=self.user,
            date=timezone.datetime(self.year, self.month, 15).date(),
            body_weight=150.0,
            body_fat=15.0,
        )

    def test_formatday_with_logs(self):
        result = self.calendar.formatday(15, 5)
        self.assertIn("exercise-icon", result)
        self.assertIn("steps-icon", result)
        self.assertIn("monitor_weight-icon", result)

    def test_formatday_without_logs(self):
        result = self.calendar.formatday(10, 3)
        self.assertNotIn("exercise-icon", result)
        self.assertNotIn("monitor_weight-icon", result)
        self.assertNotIn("steps-icon", result)

    def test_formatmonth(self):
        result = self.calendar.formatmonth(self.year, self.month)
        self.assertIn("navigate_before", result)
        self.assertIn("navigate_next", result)
        self.assertIn("month p-0_2", result)
