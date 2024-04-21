from django.test import TestCase
from django.urls import reverse
from users.models import User

from unittest.mock import patch
from common.test_globals import CREATE_USER
import json
from django.http import JsonResponse
from workout.models import Workout


# class TestViews(TestCase):
#     fixtures = ["default.json"]
#
#     def setUp(self):
#         self.user = User.objects.create_user(CREATE_USER)
#         self.client.force_login(self.user)
#
#
# class TestAddSetView(TestViews):
#
#     def test_add_set(self):
#         response = self.client.get(reverse("add_set"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed("workout/add_set.html")
#
#
# class TestAddExerciseView(TestViews):
#     def test_add_exercise(self):
#         response = self.client.get(
#             reverse("add_exercise", kwargs={"exercise": "Low Bar Squat"})
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed("workout/exercise.html")
#         self.assertEqual(response.context["exercise"]["name"], "Low Bar Squat")
#         self.assertEqual(
#             response.context["exercise"]["sets"], [{"weight": "", "reps": ""}]
#         )
#
#
# class TestWorkoutView(TestViews):
#     def test_get(self):
#         response = self.client.get("/")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "base/index.html")
#
#     def test_get_ajax(self):
#         response = self.client.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "workout/workout_session.html")
#
#
# class TestSelectWorkoutView(TestViews):
#
#     def test_get(self):
#         response = self.client.get(
#             reverse("select_workout", kwargs={"workout_name": "Starting Strength - A"})
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "workout/workout.html")
