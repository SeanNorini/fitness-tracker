from django.utils import timezone
from django.test import TestCase
from unittest.mock import patch, Mock
import requests
import json
from nutrition_tracker.services import Nutritionix, FoodLogService
from users.models import User
from log.models import FoodItem, FoodLog


class TestNutritionix(TestCase):

    @patch("requests.get")
    def test_search(self, mock_get):
        # Setup the mock to return a specific response
        mock_response = Mock()
        expected_dict = {"items": [{"item_name": "Apple", "calories": 95}]}
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Call the function
        response = Nutritionix.search("apple")
        self.assertEqual(response, expected_dict)

        # Ensure the request was called correctly
        mock_get.assert_called_once_with(
            "https://trackapi.nutritionix.com/v2/search/instant/",
            headers=Nutritionix.HEADERS,
            params={"query": "apple"},
        )

    @patch("requests.post")
    def test_get_item(self, mock_post):
        # Setup the mock to return a specific response
        mock_response = Mock()
        expected_dict = {"id": "12345", "name": "Banana"}
        mock_response.json.return_value = expected_dict
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call the function
        response = Nutritionix.get_item("natural", "banana")
        self.assertEqual(response, expected_dict)

        # Ensure the request was called correctly
        mock_post.assert_called_once_with(
            "https://trackapi.nutritionix.com/v2/natural/nutrients/",
            headers=Nutritionix.HEADERS,
            data=json.dumps({"query": "banana"}),
        )


class TestFoodLogService(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser", email="test@test.com")
        date_today = timezone.now().date()
        log = FoodLog.objects.create(user=cls.user, date=date_today)
        FoodItem.objects.create(
            log_entry=log, name="Apple", calories=95, protein=0.3, carbs=25, fat=0.2
        )

    def test_get_user_food_summary_no_logs(self):
        user_with_no_logs = User.objects.create(
            username="emptyuser", email="other@test.com"
        )
        summary = FoodLogService.get_user_food_summary(user_with_no_logs)
        expected_summary = {
            "bar_graph_data": {"dates": [], "Calories": []},
            "pie_chart_data": [],
        }
        self.assertDictEqual(summary, expected_summary)

    def test_get_user_food_summary_with_logs(self):
        summary = FoodLogService.get_user_food_summary(self.user)
        self.assertIsNotNone(summary)
        self.assertEqual(summary["avg_calories"], 95)
        self.assertEqual(summary["avg_protein"], 0.3)
        self.assertEqual(summary["avg_carbs"], 25)
        self.assertEqual(summary["avg_fat"], 0.2)
