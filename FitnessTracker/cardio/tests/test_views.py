from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from bs4 import BeautifulSoup
from users.models import User, UserSettings
from cardio.views import CardioTemplateView
from common.test_utils import elements_exist


class TestCardioView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser")
        UserSettings.objects.create(user=self.user)
        self.client.force_login(user=self.user)
        self.response = self.client.get(reverse("cardio"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def test_cardio_view_context_data(self):
        request = self.factory.get("/")
        request.user = self.user
        response = CardioTemplateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("cardio/cardio.html")

    def test_cardio_view_fetch_request(self):
        request = self.factory.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        request.user = self.user
        response = CardioTemplateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("cardio/cardio.html")

    def test_cardio_view_regular_request(self):
        request = self.factory.get("/")
        request.user = self.user
        response = CardioTemplateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/index.html")

    def test_title(self):
        self.response = self.client.get(reverse("cardio"))
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        title_tag = self.soup.find("title")
        self.assertIsNotNone(title_tag, "Title tag not found")
        self.assertEqual(title_tag.text, "Fitness Tracker - Cardio")

    def test_elements_exist(self):
        elements = {
            "class": ["summary"],
            "id": ["week", "month", "year", "save-cardio-session", "cardio-chart"],
        }
        self.assertTrue(elements_exist(elements))


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
