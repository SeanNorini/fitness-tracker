from freezegun import freeze_time
from cardio.utils import get_start_dates, format_duration
from django.test import TestCase
from django.utils import timezone

class TestIntegrationUtils(TestCase):
    @freeze_time("2024-04-01")
    def test_get_start_dates_for_week(self):
        today = timezone.now().date()
        expected = {
            "start_date": today,
            "previous_start_date": today - timezone.timedelta(days=1),
            "extended_start_date": today - timezone.timedelta(days=6),
        }
        assert get_start_dates(today, "week") == expected

    @freeze_time("2024-04-01")
    def test_get_start_dates_for_month(self):
        today = timezone.now().date()
        expected = {
            "start_date": today - timezone.timedelta(days=30),
            "previous_start_date": today - timezone.timedelta(days=60),
            "extended_start_date": today - timezone.timedelta(days=180),
        }
        assert get_start_dates(today, "month") == expected

    @freeze_time("2024-04-01")
    def test_get_start_dates_for_year(self):
        today = timezone.now().date()
        expected = {
            "start_date": today - timezone.timedelta(days=365),
            "previous_start_date": today - timezone.timedelta(days=730),
            "extended_start_date": today.replace(year=today.year - 100),
        }
        assert get_start_dates(today, "year") == expected

    def test_format_duration(self):
        with self.subTest("Under 1 hour"):
            formatted_duration = format_duration(610)
            self.assertEqual(formatted_duration, "10' 10\"")
        with self.subTest("Over 1 hour"):
            formatted_duration = format_duration(3661)
            self.assertEqual(formatted_duration, "1h 01' 01\"")
