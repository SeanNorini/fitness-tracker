from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from unittest.mock import patch


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
        self.assertIn("modules", response.context)

    def test_get_fetch_request(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "nutrition_tracker/nutrition.html")


class TestFetchNutritionSearchAPIView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.url = reverse("fetch_nutrition_search", kwargs={"query": "apple"})

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
            "fetch_item_details", kwargs={"item_type": "food", "item_id": "12345"}
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
        self.url = reverse("get_nutrition_summary")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authentication_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("nutrition_tracker.views.FoodLogService.get_user_food_summary")
    def test_successful_data_retrieval(self, mock_get_summary):
        mock_get_summary.return_value = {
            "avg_protein": 50,
            "avg_carbs": 150,
            "avg_calories": 2000,
            "avg_fat": 80,
            "pie_chart": "Some pie chart data",
            "bar_chart": "Some bar chart data",
        }
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data,
            {
                "avg_protein": 50,
                "avg_carbs": 150,
                "avg_calories": 2000,
                "avg_fat": 80,
                "pie_chart": "Some pie chart data",
                "bar_chart": "Some bar chart data",
            },
        )

    @patch("nutrition_tracker.views.FoodLogService.get_user_food_summary")
    def test_no_data_available(self, mock_get_summary):
        mock_get_summary.return_value = None
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data)
