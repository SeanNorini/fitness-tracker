from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from common.test_utils import ViewSharedTests
from unittest.mock import patch


class TestCardioTemplateView(ViewSharedTests, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("cardio")
        cls.title = "Fitness Tracker"
        cls.elements = [
            {"class": "summary"},
            {"id": "week"},
            {"id": "month"},
            {"id": "year"},
            {"id": "save-cardio-session"},
            {"id": "cardio-chart"},
        ]
        cls.regular_template = "base/index.html"
        cls.fetch_template = "cardio/cardio.html"

    def test_cardio_view_context_data(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            self.response.context["template_content"], "cardio/cardio.html"
        )
        self.assertTemplateUsed("cardio/cardio.html")


class TestCardioLogSummariesAPIView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_cardio_log_summaries(self):
        url = reverse("cardio_log_summaries", kwargs={"selected_range": "week"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summaries", response.data)
        self.assertIn("graph", response.data)

    def test_cardio_log_summaries_get(self):
        url = reverse("cardio_log_summaries", kwargs={"selected_range": "week"})
        with patch("cardio.views.get_cardio_log_summaries") as mock_get_summaries:
            mock_get_summaries.return_value = ["Summaries", "Graph"]
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("summaries", response.data)
            self.assertIn("graph", response.data)
