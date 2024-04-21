from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch

from common.common_utils import is_base64
from users.models import User


class TestNutritionTrackerView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.client = Client()
        self.url = reverse("nutrition_tracker")

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/user/login/?next={self.url}")

    def test_get_regular_request(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/index.html")

    def test_get_fetch_request(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "nutrition_tracker/nutrition.html")


class TestFetchNutritionSearchAPIView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.url = reverse("get_search_results", kwargs={"query": "apple"})

    @patch("nutrition_tracker.services.Nutritionix.search")
    def test_search_api(self, mock_search):
        mock_search.return_value = {"items": []}  # Mocked response
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_search.assert_called_once_with("apple")


class TestFetchItemDetailsAPIView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.url = reverse(
            "get_item_details", kwargs={"item_type": "food", "item_id": "12345"}
        )

    @patch("nutrition_tracker.services.Nutritionix.get_item")
    def test_item_details_api(self, mock_get_item):
        mock_get_item.return_value = {"id": "12345", "name": "Apple"}
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_item.assert_called_once_with("food", "12345")


class TestFetchNutritionSummaryAPIView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("get_nutrition_summary", args=["week"])
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authentication_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("nutrition_tracker.views.FoodLogService.get_user_food_summary")
    @patch("nutrition_tracker.views.Graph.plot_pie_chart")
    @patch("nutrition_tracker.views.Graph.plot_graph")
    def test_successful_data_retrieval(
        self, mock_plot_graph, mock_plot_pie_chart, mock_get_summary
    ):
        # Setup mock return values
        mock_get_summary.return_value = {
            "avg_protein": 50,
            "avg_carbs": 150,
            "avg_calories": 2000,
            "avg_fat": 80,
            "pie_chart_data": ["30%", "50%", "20%"],
            "bar_graph_data": [100, 200, 300],
        }
        mock_plot_graph.return_value = "Graph image data"
        mock_plot_pie_chart.return_value = "Pie chart image data"

        # Call the API
        response = self.client.get(self.url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                "avg_protein": 50,
                "avg_carbs": 150,
                "avg_calories": 2000,
                "avg_fat": 80,
                "pie_chart_data": ["30%", "50%", "20%"],
                "bar_graph_data": [100, 200, 300],
                "pie_chart": "Pie chart image data",
                "bar_chart": "Graph image data",
            },
        )

        # Check that mocks were called correctly
        mock_get_summary.assert_called_once_with(self.user)
        mock_plot_graph.assert_called_once_with()
        mock_plot_pie_chart.assert_called_once_with(
            ["Protein", "Carbs", "Fat"], ["30%", "50%", "20%"]
        )

    @patch("nutrition_tracker.views.FoodLogService.get_user_food_summary")
    def test_no_data_available(self, mock_get_summary):
        mock_get_summary.return_value = {
            "bar_graph_data": {"dates": [], "Calories": []},
            "pie_chart_data": [],
        }
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(is_base64(response.data["bar_chart"]))
