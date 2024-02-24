from django.test import TestCase
from django.urls import reverse
from users.models import User
from ..forms import WorkoutSessionForm
from unittest.mock import patch
from common.test_globals import CREATE_USER
import json
from django.http import JsonResponse
from workout.models import Workout


class TestViews(TestCase):
    fixtures = ["default.json"]

    def setUp(self):
        self.user = User.objects.create_user(CREATE_USER)
        self.client.force_login(self.user)


class TestSaveWorkoutSessionView(TestViews):

    def setUp(self) -> None:
        super().setUp()
        exercises = json.dumps({"test exercise": []})
        self.workout = {
            "name": "Starting Strength - A",
            "exercises": exercises,
            "date": "2021-01-11",
        }
        self.form = WorkoutSessionForm(data=self.workout)

    def test_valid_form(self):
        with patch("workouts.views.save_workout_session") as save_workout_session:
            response = self.client.post(
                reverse("save_workout_session"), data=self.workout
            )

            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response, JsonResponse)
            self.assertTrue(self.form.is_valid())
            save_workout_session.assert_called_once()
            called_user_id = save_workout_session.call_args[0][0].id
            self.assertEqual(called_user_id, self.user.id)
            called_form = save_workout_session.call_args[0][1]
            self.assertEqual(called_form.cleaned_data, self.form.cleaned_data)
            self.assertJSONEqual(response.content, {"success": True})

    def test_invalid_form(self):
        del self.workout["name"]
        response = self.client.post(reverse("save_workout_session"), data=self.workout)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertJSONEqual(response.content, {"error": "Invalid Form"})


class TestAddSetView(TestViews):

    def test_add_set(self):
        response = self.client.get(reverse("add_set"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("workout/add_set.html")


class TestAddExerciseView(TestViews):
    def test_add_exercise(self):
        response = self.client.get(
            reverse("add_exercise", kwargs={"exercise": "Low Bar Squat"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("workout/exercise.html")
        self.assertEqual(response.context["exercise"]["name"], "Low Bar Squat")
        self.assertEqual(
            response.context["exercise"]["sets"], [{"weight": "", "reps": ""}]
        )


class TestWorkoutView(TestViews):
    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/index.html")

    def test_get_ajax(self):
        response = self.client.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "workout/workout_session.html")


class TestSelectWorkoutView(TestViews):

    def test_get(self):
        response = self.client.get(
            reverse("select_workout", kwargs={"workout_name": "Starting Strength - A"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "workout/workout.html")
