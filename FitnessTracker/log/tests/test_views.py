from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.test import Client
from log.views import LogView, DailyLogView
from users.models import User, UserSettings
from workout.models import Workout, Exercise
from rest_framework import status
from log.models import WeightLog, CardioLog, WorkoutLog


class TestLogView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser")
        self.client.force_login(user=self.user)
        self.user_settings = UserSettings.objects.create(user=self.user)
        self.workout = Workout.objects.create(user=self.user, name="Test Workout")
        WorkoutLog.objects.create(
            user=self.user,
            date="2024-04-01",
            total_time=60,
            workout=self.workout,
        )
        WeightLog.objects.create(
            user=self.user,
            date="2024-04-01",
            body_weight=150,
            body_fat=20,
        )

    def test_log_view_with_valid_date(self):
        # Create a URL with a valid year and month
        url = reverse("log", kwargs={"year": "2024", "month": "4"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/index.html")

    def test_log_view_with_invalid_date(self):
        # Create a URL with an invalid month
        url = reverse("log", kwargs={"year": "2024", "month": "13"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/index.html")
        # Check if default month and year are used
        year = timezone.now().year
        month = timezone.now().month
        self.assertEqual(year, response.context["year"])
        self.assertEqual(month, response.context["month"])

    def test_log_view_fetch_request(self):
        url = reverse("log", kwargs={"year": "2024", "month": "4"})
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "log/log.html")
        self.assertIn("calendar", response.context)

    def test_log_view_user_not_authenticated(self):
        self.client.logout()
        url = reverse("log")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/user/login/?next={url}")

    def test_response_content_for_correct_data(self):
        url = reverse("log", kwargs={"year": "2024", "month": "4"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["workout_logs"]), 1)
        self.assertEqual(len(response.context["weight_logs"]), 1)

    def test_get_date_with_valid_params(self):
        request = self.factory.get("/fake-url/", {"year": "2024", "month": "4"})
        view = LogView()
        view.kwargs = {"year": "2024", "month": "4"}
        year, month = view.get_date()
        self.assertEqual(year, 2024)
        self.assertEqual(month, 4)

    def test_get_date_with_invalid_params(self):
        view = LogView()
        view.kwargs = {"year": "abcd", "month": "efgh"}  # Non-integer values
        year, month = view.get_date()
        self.assertEqual(year, timezone.now().year)
        self.assertEqual(month, timezone.now().month)

    def test_get_date_with_out_of_range_month(self):
        view = LogView()
        view.kwargs = {"year": "2024", "month": "13"}  # Invalid month
        year, month = view.get_date()
        self.assertEqual(year, timezone.now().year)
        self.assertEqual(month, timezone.now().month)

    def test_get_workout_logs(self):
        view = LogView()
        view.request = self.factory.get("/fake-url/")
        view.request.user = self.user
        logs = view.get_workout_logs(self.user, 2024, 4)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.first().total_time, 60)

    def test_get_weight_logs(self):
        view = LogView()
        view.request = self.factory.get("/fake-url/")
        view.request.user = self.user
        logs = view.get_weight_logs(self.user, 2024, 4)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.first().body_weight, 150)
        self.assertEqual(logs.first().body_fat, 20)


class DailyLogViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_login(user=self.user)

        self.date = "2024-4-11"
        self.workout = Workout.objects.create(user=self.user, name="Test Workout")
        self.workout_log = WorkoutLog.objects.create(
            user=self.user, date=self.date, total_time=60, workout=self.workout
        )
        self.weight_log = WeightLog.objects.create(
            user=self.user, date=self.date, body_weight=150, body_fat=20
        )

    def test_daily_log_view(self):
        url = reverse("daily_log", kwargs={"year": "2024", "month": "4", "day": "11"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Check context data passed to the template
        self.assertEqual(response.context["year"], "2024")
        self.assertEqual(response.context["month"], "4")
        self.assertEqual(response.context["day"], "11")
        self.assertEqual(response.context["month_name"], "April")

        # Assert workout logs are correctly passed in the context
        self.assertIn("workout_logs", response.context)
        self.assertEqual(len(response.context["workout_logs"]), 1)

        # Check correct serialization if WorkoutLogSerializer is used in the view
        self.assertEqual(response.context["workout_logs"][0]["total_time"], 60)

        # Assert weight logs are correctly passed in the context
        self.assertIn("weight_log", response.context)
        self.assertEqual(response.context["weight_log"], self.weight_log)

    def test_log_view_user_not_authenticated(self):
        self.client.logout()
        url = reverse("daily_log")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/user/login/?next={url}")


class DeleteWeightLogAPITests(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username="user1", password="12345")
        self.user2 = User.objects.create_user(
            username="user2", password="12345", email="fake@gmail.com"
        )

        # Create weight logs for each user
        self.weight_log1 = WeightLog.objects.create(
            user=self.user1, date=timezone.now(), body_weight=160, body_fat=20
        )
        self.weight_log2 = WeightLog.objects.create(
            user=self.user2, date=timezone.now(), body_weight=150, body_fat=18
        )

    def test_delete_weight_log_unauthorized(self):
        # User2 tries to delete User1's weight log
        self.client.login(username="user2", password="12345")
        url = reverse("delete_weight_log", args=[self.weight_log1.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(WeightLog.objects.count(), 2)  # Ensure the log was not deleted

    def test_delete_weight_log_authorized(self):
        # User1 deletes their own weight log
        self.client.login(username="user1", password="12345")
        url = reverse("delete_weight_log", args=[self.weight_log1.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(WeightLog.objects.count(), 1)  # One log should be deleted
        self.assertNotIn(self.weight_log1, WeightLog.objects.all())

    def test_delete_weight_log_not_found(self):
        # Test deleting a non-existing log
        self.client.login(username="user1", password="12345")
        url = reverse("delete_weight_log", args=[999])  # Non-existing ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(WeightLog.objects.count(), 2)  # No logs should be deleted


class TestCreateCardioLogAPIView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("create_cardio_log")

    def test_create_cardio_log(self):
        data = {
            "datetime": "2024-04-12T01:17:38.246Z",
            "duration-minutes": "30",
            "distance-integer": "5",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CardioLog.objects.count(), 1)
        self.assertEqual(CardioLog.objects.first().distance, 5.0)


class UpdateWorkoutLogTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="testpass")
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass"
        )
        self.workout = Workout.objects.create(name="Morning Routine", user=self.user)
        self.exercise = Exercise.objects.create(name="Push Up", user=self.user)
        self.workout_log = WorkoutLog.objects.create(
            user=self.user, workout=self.workout
        )
        self.url = reverse("update_workout_log", kwargs={"pk": self.workout_log.pk})

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_user_access_own_log(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_other_user_log(self):
        self.client.login(username="otheruser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_context_data(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)
        self.assertIn("workout", response.context)
        self.assertEqual(response.context["workout"]["id"], self.workout_log.pk)

        self.assertIn("workouts", response.context)
        self.assertIn("exercises", response.context)
        self.assertEqual(
            len(response.context["workouts"]),
            Workout.objects.filter(user=self.user).count(),
        )
        self.assertEqual(
            len(response.context["exercises"]),
            Exercise.objects.filter(user=self.user).count(),
        )

    def test_template_content(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)
        self.assertContains(response, self.workout_log.workout.name)
        self.assertContains(
            response, "Push Up"
        )  # Assuming the template displays exercise names
