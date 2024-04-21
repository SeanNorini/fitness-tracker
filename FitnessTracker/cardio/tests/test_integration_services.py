from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import datetime
from freezegun import freeze_time
from cardio.services import get_cardio_log_averages, get_cardio_log_summaries
from log.models import CardioLog
from users.models import User, UserSettings
from common.test_globals import CREATE_USER
import base64


class TestIntegrationServices(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(**CREATE_USER)
        self.user_settings = UserSettings.objects.create(
            user=self.user, body_weight=160
        )

    def test_get_cardio_log_averages(self) -> None:
        with self.subTest("Count is greater than zero"):
            log = {"total_distance": 4, "total_duration": 3602, "count": 2}
            log_averages = get_cardio_log_averages(log, self.user)
            self.assertEqual(log_averages["average_distance"], 2)
            self.assertEqual(log_averages["average_duration"], "30' 01\"")
            self.assertEqual(log_averages["calories_burned"], 401)

        with self.subTest("Count is zero"):
            log = {"total_distance": 4, "total_duration": 3661, "count": 0}
            log_averages = get_cardio_log_averages(log, self.user)
            self.assertEqual(log_averages["average_distance"], 0)
            self.assertEqual(log_averages["average_duration"], 0)
            self.assertEqual(log_averages["calories_burned"], 0)

    @freeze_time("2024-04-18 12:00:00")
    def test_get_cardio_log_summaries(self) -> None:
        today = timezone.now()
        CardioLog.objects.create(
            user=self.user, datetime=today, duration=timedelta(seconds=1800), distance=3
        )
        CardioLog.objects.create(
            user=self.user,
            datetime=(today - timedelta(days=1)),
            duration=timedelta(seconds=1800),
            distance=3,
        )
        CardioLog.objects.create(
            user=self.user,
            datetime=(today - timedelta(days=6)),
            duration=timedelta(seconds=1800),
            distance=3,
        )
        cardio_log_summaries, graph = get_cardio_log_summaries(self.user, "week")

        expected_summaries = [
            {
                "total_distance": 3.0,
                "total_duration": 1800.0,
                "count": 1,
                "average_distance": 3.0,
                "average_duration": "30' 00\"",
                "calories_burned": 601,
                "pace": "10' 00\"",
            },
            {
                "total_distance": 3.0,
                "total_duration": 1800.0,
                "count": 1,
                "average_distance": 3.0,
                "average_duration": "30' 00\"",
                "calories_burned": 601,
                "pace": "10' 00\"",
            },
            {
                "total_distance": 9.0,
                "total_duration": 5400.0,
                "count": 3,
                "average_distance": 3.0,
                "average_duration": "30' 00\"",
                "calories_burned": 601,
                "pace": "10' 00\"",
            },
        ]

        self.assertEqual(expected_summaries, cardio_log_summaries)
        try:
            base64_bytes = base64.b64decode(graph, validate=True)
            is_base64 = True
        except Exception:
            is_base64 = False

        self.assertTrue(is_base64, "The string is not a valid base64 encoded string.")
