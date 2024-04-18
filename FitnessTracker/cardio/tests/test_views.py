from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from log.models import CardioLog
from users.models import User, UserSettings
from cardio.views import CardioTemplateView


class TestCardioView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser")
        UserSettings.objects.create(user=self.user)

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


class TestGetCardioLogSummariesAPIView(TestCase):
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
