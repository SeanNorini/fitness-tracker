from datetime import timedelta

from log.models import CardioLog
from cardio.services import (
    update_log_dict_and_graph_data,
    get_cardio_log_averages,
    get_cardio_logs_grouped_by_day,
    add_start_end_dates_to_graph_data,
    get_cardio_log_summaries,
    aggregate_cardio_logs,
)
from django.utils import timezone
from django.test import TestCase
from unittest.mock import patch, MagicMock, PropertyMock, call
from users.models import User


class TestUpdateLogDictAndGraphData(TestCase):

    def test_update_log_dict(self):
        log_dict = {"total_distance": 0, "total_duration": 0, "count": 0}
        log = {
            "total_distance": 5,
            "total_duration": timedelta(minutes=30),
            "day": timezone.now(),
        }

        update_log_dict_and_graph_data(log_dict, None, log, False)

        self.assertEqual(log_dict["total_distance"], 5)
        self.assertEqual(log_dict["total_duration"], 1800)  # 30 minutes in seconds
        self.assertEqual(log_dict["count"], 1)

    def test_update_graph_data(self):
        log_dict = {"total_distance": 0, "total_duration": 0, "count": 0}
        graph_data = {"dates": [], "distances": []}
        log = {
            "total_distance": 5,
            "total_duration": timedelta(minutes=30),
            "day": timezone.now(),
        }

        update_log_dict_and_graph_data(log_dict, graph_data, log, True)

        self.assertEqual(graph_data["dates"][0], log["day"].date())
        self.assertEqual(graph_data["distances"][0], 5)

    def test_do_not_update_graph_data_when_flag_is_false(self):
        log_dict = {"total_distance": 0, "total_duration": 0, "count": 0}
        graph_data = {"dates": [], "distances": []}
        log = {
            "total_distance": 5,
            "total_duration": timedelta(minutes=30),
            "day": timezone.now(),
        }

        update_log_dict_and_graph_data(log_dict, graph_data, log, False)

        self.assertEqual(len(graph_data["dates"]), 0)
        self.assertEqual(len(graph_data["distances"]), 0)

    def test_no_graph_data_provided(self):
        log_dict = {"total_distance": 0, "total_duration": 0, "count": 0}
        log = {
            "total_distance": 5,
            "total_duration": timedelta(minutes=30),
            "day": timezone.now(),
        }

        update_log_dict_and_graph_data(log_dict, None, log, True)

        # Expecting no errors and that the log_dict still updates correctly
        self.assertEqual(log_dict["total_distance"], 5)
        self.assertEqual(log_dict["total_duration"], 1800)
        self.assertEqual(log_dict["count"], 1)


class TestGetCardioLogAverages(TestCase):
    def test_count_and_distance_is_zero(self):
        log = {"total_distance": 0, "total_duration": 0, "count": 0}
        log = get_cardio_log_averages(log, None)
        self.assertDictEqual(
            {
                "total_distance": 0,
                "total_duration": 0,
                "count": 0,
                "average_distance": 0,
                "average_duration": 0,
                "calories_burned": 0,
                "pace": "N/A",
            },
            log,
        )

    def test_distance_greater_than_zero(self):
        log = {"total_distance": 1, "total_duration": 1, "count": 0}
        with patch("cardio.services.format_duration") as mock_format_duration:
            mock_format_duration.return_value = True
            log = get_cardio_log_averages(log, None)
            self.assertEqual(log["pace"], True)
            mock_format_duration.assert_called_once_with(1)

    @patch("cardio.services.format_duration")
    @patch("cardio.services.get_calories_burned")
    def test_log_update_with_count_greater_than_zero(
        self, mock_get_calories_burned, mock_format_duration
    ):
        # Create a mock user
        mock_user = MagicMock()
        type(mock_user).distance_unit = PropertyMock(return_value="mi")
        type(mock_user).body_weight = PropertyMock(return_value=150)
        mock_get_calories_burned.return_value = 1000

        # Expected data to pass
        log = {"total_distance": 100, "total_duration": 10000, "count": 5}
        updated_log = get_cardio_log_averages(log, mock_user)

        # Assertions to check the updated log
        self.assertEqual(updated_log["average_distance"], 20)
        self.assertEqual(updated_log["calories_burned"], 200)
        expected_calls = [
            call(2000),  # 10000 total_duration / 5 count
            call(100),  # 10000 total_duration / 100 total_distance
        ]
        mock_format_duration.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(mock_format_duration.call_count, 2)
        mock_get_calories_burned.assert_called_once_with("mi", 100, 150)


class TestGetCardioLogsGroupByDay(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

        today = timezone.now()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        CardioLog.objects.create(
            user=self.user, datetime=today, distance=5, duration=timedelta(seconds=2500)
        )
        CardioLog.objects.create(
            user=self.user, datetime=today, distance=3, duration=timedelta(seconds=2000)
        )
        CardioLog.objects.create(
            user=self.user,
            datetime=yesterday,
            distance=2,
            duration=timedelta(seconds=1500),
        )
        CardioLog.objects.create(
            user=self.user,
            datetime=two_days_ago,
            distance=10,
            duration=timedelta(seconds=1800),
        )

    def test_get_cardio_logs_grouped_by_day(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        start_date = two_days_ago
        end_date = today

        logs = get_cardio_logs_grouped_by_day(self.user, start_date, end_date)
        result = list(logs)

        # Check the number of days returned
        self.assertEqual(len(result), 3)

        # Check the calculations and grouping
        expected_results = [
            {
                "day": two_days_ago,
                "total_distance": 10,
                "total_duration": timedelta(seconds=1800),
            },
            {
                "day": yesterday,
                "total_distance": 2,
                "total_duration": timedelta(seconds=1500),
            },
            {
                "day": today,
                "total_distance": 8,
                "total_duration": timedelta(seconds=4500),
            },
        ]

        for expected, log_day in zip(expected_results, result):
            self.assertEqual(log_day["day"].date(), expected["day"])
            self.assertEqual(log_day["total_distance"], expected["total_distance"])
            self.assertEqual(log_day["total_duration"], expected["total_duration"])


class TestAddStartEndDatesToGraphData(TestCase):
    def setUp(self):
        self.start = timezone.now() - timedelta(days=10)
        self.end = timezone.now()
        self.graph_data = {"dates": [], "distances": []}

    def test_graph_data_empty(self):
        add_start_end_dates_to_graph_data(self.graph_data, self.start, self.end)
        self.assertEqual(len(self.graph_data["dates"]), 2)
        self.assertEqual(self.graph_data["dates"][0], self.start)
        self.assertEqual(self.graph_data["dates"][1], self.end)

    def test_graph_data_one_day(self):
        day = self.end - timedelta(days=1)
        self.graph_data.update({"dates": [day], "distances": [10]})
        add_start_end_dates_to_graph_data(self.graph_data, self.start, self.end)
        self.assertEqual(len(self.graph_data["dates"]), 3)
        self.assertDictEqual(
            self.graph_data,
            {"dates": [self.start, day, self.end], "distances": [0, 10, 0]},
        )

    def test_graph_data_start_and_end_exist(self):
        self.graph_data = {"dates": [self.start, self.end], "distances": [5, 10]}
        add_start_end_dates_to_graph_data(self.graph_data, self.start, self.end)
        self.assertEqual(len(self.graph_data["dates"]), 2)
        self.assertDictEqual(
            self.graph_data, {"dates": [self.start, self.end], "distances": [5, 10]}
        )


class TestGetCardioLogSummaries(TestCase):
    def setUp(self):
        self.user = MagicMock()
        self.selected_range = "week"
        self.today = timezone.now().date()

    @patch("cardio.services.get_start_dates")
    @patch("cardio.services.get_cardio_logs_grouped_by_day")
    @patch("cardio.services.aggregate_cardio_logs")
    @patch("cardio.services.add_start_end_dates_to_graph_data")
    @patch("cardio.services.get_cardio_log_averages")
    def test_get_cardio_log_summaries(
        self,
        mock_get_cardio_log_averages,
        mock_add_start_end_dates_to_graph_data,
        mock_aggregate_cardio_logs,
        mock_get_cardio_logs_grouped_by_day,
        mock_get_start_dates,
    ):
        # Setup mock returns
        mock_get_start_dates.return_value = {
            "extended_start_date": self.today - timezone.timedelta(days=10),
            "start_date": self.today - timezone.timedelta(days=7),
        }
        mock_get_cardio_logs_grouped_by_day.return_value = [
            {"day": self.today, "total_distance": 100, "total_duration": 60}
        ]
        mock_aggregate_cardio_logs.return_value = (
            [{"total_distance": 100, "total_duration": 60}],
            {"dates": [], "distances": []},
        )
        mock_get_cardio_log_averages.return_value = {
            "average_distance": 10,
            "average_duration": 6,
        }

        # Execute the function
        result, graph_data = get_cardio_log_summaries(self.user, self.selected_range)

        # Asserts
        mock_get_start_dates.assert_called_once_with(self.today, self.selected_range)
        mock_get_cardio_logs_grouped_by_day.assert_called_once()
        mock_aggregate_cardio_logs.assert_called_once()
        mock_add_start_end_dates_to_graph_data.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)
        self.assertIsInstance(graph_data, dict)


class TestAggregateCardioLogs(TestCase):
    def setUp(self):
        self.today = timezone.now()
        self.start_dates = {
            "start_date": (self.today - timezone.timedelta(days=1)).date(),
            "previous_start_date": (self.today - timezone.timedelta(days=8)).date(),
            "extended_start_date": (self.today - timezone.timedelta(days=15)).date(),
        }

    @patch("cardio.services.update_log_dict_and_graph_data")
    def test_aggregate_cardio_logs(self, mock_update_log_dict_and_graph_data):
        def side_effect(log_dict, graph_data, log, update_graph):
            log_dict.update(
                {
                    "total_distance": log_dict.get("total_distance", 0)
                    + log["total_distance"],
                    "total_duration": log_dict.get("total_duration", 0)
                    + log["total_duration"],
                    "count": log_dict.get("count", 0) + 1,
                }
            )
            if update_graph:
                graph_data["dates"].append(log["day"].date())
                graph_data["distances"].append(log["total_distance"])

        mock_update_log_dict_and_graph_data.side_effect = side_effect

        # Sample log data
        logs = [
            {"day": self.today, "total_distance": 10, "total_duration": 30},  # current
            {
                "day": self.today - timezone.timedelta(days=3),
                "total_distance": 5,
                "total_duration": 15,
            },  # previous
            {
                "day": self.today - timezone.timedelta(days=10),
                "total_distance": 20,
                "total_duration": 60,
            },  # extended
        ]

        # Call the function
        aggregates, graph_data = aggregate_cardio_logs(logs, self.start_dates, "week")

        # Assertions
        self.assertEqual(aggregates[0]["total_distance"], 10)
        self.assertEqual(aggregates[1]["total_distance"], 5)
        self.assertEqual(aggregates[2]["total_distance"], 35)
        self.assertEqual(len(graph_data["dates"]), 3)
