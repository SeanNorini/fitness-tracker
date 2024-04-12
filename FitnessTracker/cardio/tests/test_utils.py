from datetime import timedelta

from cardio.utils import *
from django.test import TestCase
from unittest.mock import patch


class TestUtils(TestCase):
    def test_get_time_from_duration(self):
        with self.subTest("Less than 0 duration"):
            hours, minutes, seconds = get_time_from_duration(-1)
            self.assertEqual(hours, 0)
            self.assertEqual(minutes, 0)
            self.assertEqual(seconds, 0)

        with self.subTest("0 duration"):
            hours, minutes, seconds = get_time_from_duration(0)
            self.assertEqual(hours, 0)
            self.assertEqual(minutes, 0)
            self.assertEqual(seconds, 0)

        with self.subTest("1 hour, 1 minute, 1 second"):
            hours, minutes, seconds = get_time_from_duration(3661)
            self.assertEqual(hours, 1)
            self.assertEqual(minutes, 1)
            self.assertEqual(seconds, 1)
            self.assertIsInstance(hours, int)
            self.assertIsInstance(minutes, int)
            self.assertIsInstance(seconds, int)

    def test_format_duration(self):
        with self.subTest("1 hour, 1 minute, 1 second"):
            with patch(
                "cardio.utils.get_time_from_duration"
            ) as mock_get_time_from_duration:
                mock_get_time_from_duration.return_value = (1, 1, 1)
                formatted_duration = format_duration(None)
                self.assertEqual(formatted_duration, "1h 01' 01\"")

        with self.subTest("1 minute, 1 second"):
            with patch(
                "cardio.utils.get_time_from_duration"
            ) as mock_get_time_from_duration:
                mock_get_time_from_duration.return_value = (0, 1, 1)
                formatted_duration = format_duration(None)
                self.assertEqual(formatted_duration, "1' 01\"")

        with self.subTest("Integration with get_time_from_duration"):
            formatted_duration = format_duration(3661)
            self.assertEqual(formatted_duration, "1h 01' 01\"")

    def test_get_calories_burned(self):
        with self.subTest("calories burned with mi unit"):
            calories_burned = get_calories_burned("mi", 1, 100)
            self.assertEqual(calories_burned, 125)  # should be 125.4 truncated to 125

        with self.subTest("calories burned with mi unit"):
            calories_burned = get_calories_burned("km", 1, 100)
            self.assertEqual(calories_burned, 103)  # should be 103.6 truncated to 103

    def test_get_start_dates(self):
        with self.subTest("Get week"):
            with patch(
                "cardio.utils.get_start_dates_for_week"
            ) as mock_get_start_dates_for_week:
                mock_get_start_dates_for_week.return_value = 0
                start_dates = get_start_dates(0, "week")
                self.assertEqual(start_dates, 0)
                mock_get_start_dates_for_week.assert_called_once_with(0)

        with self.subTest("Get month"):
            with patch(
                "cardio.utils.get_start_dates_for_month"
            ) as mock_get_start_dates_for_week:
                mock_get_start_dates_for_week.return_value = 0
                start_dates = get_start_dates(0, "month")
                self.assertEqual(start_dates, 0)
                mock_get_start_dates_for_week.assert_called_once_with(0)

        with self.subTest("Get week"):
            with patch(
                "cardio.utils.get_start_dates_for_year"
            ) as mock_get_start_dates_for_week:
                mock_get_start_dates_for_week.return_value = 0
                start_dates = get_start_dates(0, "year")
                self.assertEqual(start_dates, 0)
                mock_get_start_dates_for_week.assert_called_once_with(0)

    def test_get_start_dates_for_week(self):
        today = timezone.now()
        dates = get_start_dates_for_week(today)
        self.assertEqual(dates["start_date"].date(), today.date())
        self.assertEqual(
            dates["previous_start_date"].date(),
            (today - timezone.timedelta(days=1)).date(),
        )
        self.assertEqual(
            dates["extended_start_date"].date(),
            (today - timezone.timedelta(days=6)).date(),
        )

    def test_get_start_dates_for_month(self):
        today = timezone.now()
        dates = get_start_dates_for_month(today)
        self.assertEqual(
            dates["start_date"].date(), (today - timezone.timedelta(days=30)).date()
        )
        self.assertEqual(
            dates["previous_start_date"].date(),
            (today - timezone.timedelta(days=60)).date(),
        )
        self.assertEqual(
            dates["extended_start_date"].date(),
            (today - timezone.timedelta(days=180)).date(),
        )

    def test_get_start_dates_for_year(self):
        today = timezone.now()
        dates = get_start_dates_for_year(today)
        self.assertEqual(
            dates["start_date"].date(), (today - timezone.timedelta(days=365)).date()
        )
        self.assertEqual(
            dates["previous_start_date"].date(),
            (today - timezone.timedelta(days=730)).date(),
        )
        self.assertEqual(
            dates["extended_start_date"].date(),
            today.replace(year=today.year - 100).date(),
        )
