from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.test import Client
from rest_framework.test import APIClient, APITestCase
from datetime import timedelta, date
from bs4 import BeautifulSoup
from log.views import LogView
from users.models import User, UserSettings
from workout.models import Workout, Exercise
from rest_framework import status
from log.models import WeightLog, CardioLog, WorkoutLog, FoodLog


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
            total_time=timedelta(hours=1),
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
        soup = BeautifulSoup(response.content, "html.parser")
        calendar_date = soup.find(id="month-name")
        self.assertEqual(calendar_date.text, date.today().strftime("%B %Y"))

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


class TestDailyLogView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_login(user=self.user)

        self.date = "2024-4-11"
        self.workout = Workout.objects.create(user=self.user, name="Test Workout")
        self.workout_log = WorkoutLog.objects.create(
            user=self.user,
            date=self.date,
            total_time=timedelta(hours=1),
            workout=self.workout,
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
        self.assertEqual(response.context["workout_logs"][0]["total_time"], "01:00:00")

        # Assert weight logs are correctly passed in the context
        self.assertIn("weight_log", response.context)
        self.assertEqual(response.context["weight_log"], self.weight_log)

    def test_log_view_user_not_authenticated(self):
        self.client.logout()
        url = reverse("daily_log")
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/user/login/?next={url}")


class TestWeightLogTemplateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")
        UserSettings.objects.create(user=self.user, body_weight=180)

    def test_template_used(self):
        response = self.client.get(reverse("weight_log_template"))
        self.assertTemplateUsed(response, "log/save_weight_log.html")

    def test_context_data(self):
        response = self.client.get(reverse("weight_log_template"))
        self.assertIn("user_settings", response.context)
        self.assertEqual(response.context["user_settings"].body_weight, 180)


class TestWeightLogViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.force_authenticate(user=self.user)
        self.weight_log = WeightLog.objects.create(
            user=self.user, body_weight=150, body_fat=15, date=timezone.now()
        )

    def test_get_queryset(self):
        response = self.client.get(reverse("weightlog-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Assuming this is the only log

    def test_create_weight_log(self):
        today = timezone.now()
        day = today.day
        year = today.year
        post_data = {
            "body_weight": 160,
            "body_fat": 14,
            "date": f"January {day}, {year}",
        }
        response = self.client.post(reverse("weightlog-list"), post_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(WeightLog.objects.count(), 2)
        self.assertEqual(WeightLog.objects.last().body_weight, 160)
        self.assertEqual(WeightLog.objects.last().body_fat, 14)


class TestWorkoutLogTemplateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.workout = Workout.objects.create(name="Morning Routine", user=self.user)
        self.workout_log = WorkoutLog.objects.create(
            user=self.user, workout=self.workout, date=timezone.now()
        )
        self.client.login(username="user", password="pass")

    def test_context_data(self):
        url = reverse("workout_log_template", kwargs={"pk": self.workout_log.pk})
        response = self.client.get(url)
        self.assertEqual(
            response.context["workout_log"]["workout_name"], "Morning Routine"
        )


class TestUpdateWorkoutLogTemplateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user", email="user@user.com", password="testpass"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass", email="other@other.com"
        )
        self.workout = Workout.objects.create(name="Morning Routine", user=self.user)
        self.exercise = Exercise.objects.create(name="Push Up", user=self.user)
        self.workout_log = WorkoutLog.objects.create(
            user=self.user, workout=self.workout
        )
        self.url = reverse(
            "update_workout_log_template", kwargs={"pk": self.workout_log.pk}
        )

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/user/login/?next={self.url}")

    def test_user_access_own_log(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_other_user_log(self):
        self.client.login(username="otheruser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.context["workout"]["user"], None)

    def test_context_data(self):
        self.client.login(username="user", password="testpass")
        response = self.client.get(self.url)
        self.assertIn("workout", response.context)
        self.assertEqual(response.context["workout"]["pk"], self.workout_log.pk)

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


class TestWorkoutLogViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user", password="pass", email="test@test.com"
        )
        self.client.login(username="user", password="pass")
        self.workout = Workout.objects.create(user=self.user, name="Test Workout")
        self.workout_log = WorkoutLog.objects.create(
            user=self.user, workout=self.workout
        )

    def test_list_workout_logs(self):
        url = reverse("workoutlog-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data), 1
        )  # Ensure only the user's logs are listed

    def test_create_workout_log(self):
        url = reverse("workoutlog-list")
        data = {
            "workout": self.workout.pk,
            "workout_name": "Test Workout",
            "date": "2024-04-01",
            "total_time": 3600,
            "workout_exercises": [
                {"bench press": {"reps": [5], "weights": [50]}},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(WorkoutLog.objects.count(), 2)

    def test_retrieve_workout_log(self):
        url = reverse("workoutlog-detail", kwargs={"pk": self.workout_log.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pk"], self.workout_log.pk)

    def test_update_workout_log(self):
        url = reverse("workoutlog-detail", kwargs={"pk": self.workout_log.pk})
        data = {"total_time": 7200}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.workout_log.refresh_from_db()
        self.assertEqual(self.workout_log.total_time, timedelta(hours=2))

    def test_delete_workout_log(self):
        url = reverse("workoutlog-detail", kwargs={"pk": self.workout_log.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)


class TestCardioLogViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cardio_log = CardioLog.objects.create(
            user=self.user,
            datetime="2024-01-01T12:00:00Z",
            duration=timedelta(minutes=30),
            distance=5.0,
        )
        self.url = reverse("cardiolog-list")

    def test_authentication_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_access_own_logs(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_cannot_access_other_user_logs(self):
        other_user = User.objects.create_user(
            username="otheruser", password="password", email="test@test.com"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_cardio_log(self):
        data = {
            "datetime": "2024-01-02T15:00:00Z",
            "duration-hours": "1",
            "duration-minutes": "15",
            "duration-seconds": "30",
            "distance-integer": "7",
            "distance-decimal": "5",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CardioLog.objects.count(), 2)
        new_log = CardioLog.objects.get(datetime="2024-01-02T15:00:00Z")
        self.assertEqual(new_log.duration, timedelta(hours=1, minutes=15, seconds=30))
        self.assertEqual(new_log.distance, 7.5)

    def test_retrieve_cardio_log(self):
        url = reverse("cardiolog-detail", kwargs={"pk": self.cardio_log.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance"], 5.0)

    def test_update_cardio_log(self):
        url = reverse("cardiolog-detail", kwargs={"pk": self.cardio_log.pk})
        data = {"distance-integer": "10", "distance-decimal": "25"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cardio_log.refresh_from_db()
        self.assertEqual(self.cardio_log.distance, 10.25)

    def test_delete_cardio_log(self):
        url = reverse("cardiolog-detail", kwargs={"pk": self.cardio_log.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CardioLog.objects.count(), 0)


class FoodLogViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@test.com"
        )
        cls.other_user = User.objects.create_user(
            username="otheruser", password="testpass", email="other@test.com"
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)
        self.food_log = FoodLog.objects.create(user=self.user, date=date.today())
        self.url_list = reverse("foodlog-list")
        self.url_detail = reverse("foodlog-detail", kwargs={"pk": self.food_log.pk})
        self.food_data = {
            "date": date.today(),
            "food_items": [
                {
                    "name": "Apple",
                    "calories": 95,
                    "protein": 0.5,
                    "carbs": 25,
                    "fat": 0.3,
                },
                {
                    "name": "Banana",
                    "calories": 105,
                    "protein": 1.3,
                    "carbs": 27,
                    "fat": 0.4,
                },
            ],
        }

    def test_authentication_required(self):
        self.client.logout()
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_access_own_logs(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_cannot_access_other_user_logs(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_food_log(self):
        response = self.client.post(self.url_list, self.food_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            FoodLog.objects.filter(user=self.user).last().food_items.count(), 2
        )

    def test_update_food_log(self):
        update_data = self.food_data
        update_data["food_items"].append(
            {
                "name": "Orange",
                "calories": 62,
                "protein": 1.2,
                "carbs": 15.4,
                "fat": 0.2,
            }
        )
        response = self.client.put(self.url_detail, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FoodLog.objects.get(pk=self.food_log.pk).food_items.count(), 3)

    def test_delete_food_log(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FoodLog.objects.filter(pk=self.food_log.pk).exists())

    def test_unique_date_per_user(self):
        response = self.client.post(self.url_list, self.food_data, format="json")
        logs = FoodLog.objects.filter(user=self.user, date=date.today())
        self.assertEqual(len(logs), 1)
