from django.test import TestCase
from users.models import User
from rest_framework.test import APIRequestFactory
from workout.models import Routine, Week, Day, Workout, Exercise, RoutineSettings
from workout.serializers import (
    RoutineSerializer,
    DaySerializer,
    WeekSerializer,
    ExerciseSerializer,
    WorkoutSerializer,
    RoutineSettingsSerializer,
)


class TestSerializers(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@test.com"
        )
        self.request_factory = APIRequestFactory()
        self.request = self.request_factory.get("/workout/workout_settings/")
        self.request.user = self.user

        self.exercise = Exercise.objects.create(
            user=self.user,
            name="Push-Up",
            five_rep_max=100,
            default_weight=50,
            default_reps=10,
        )
        self.routine = Routine.objects.create(user=self.user, name="Beginner Routine")
        self.week = Week.objects.create(routine=self.routine, week_number=1)
        self.day = Day.objects.create(week=self.week, day_number=1)
        self.workout = Workout.objects.create(user=self.user, name="Upper Body")
        self.workout.days.add(self.day)

    def test_day_serializer_create_and_representation(self):
        data = {"day_number": 2, "workouts": ["Push-Up"]}
        serializer = DaySerializer(data=data, context={"request": self.request})
        self.assertTrue(serializer.is_valid())
        day = serializer.save(week=self.week)
        self.assertEqual(day.day_number, 2)
        self.assertEqual(len(day.workouts.all()), 1)

        # Representation check
        representation = DaySerializer(day).data
        self.assertEqual(representation["workouts"][0], "Push-Up")

    def test_routine_serializer_create_and_representation(self):
        data = {
            "name": "Advanced Routine",
            "weeks": [
                {
                    "week_number": 1,
                    "days": [{"day_number": 1, "workouts": ["Push-Up"]}],
                }
            ],
        }
        serializer = RoutineSerializer(data=data, context={"request": self.request})
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        routine = serializer.save()
        self.assertEqual(routine.name, "Advanced Routine")
        self.assertEqual(routine.weeks.count(), 1)
        self.assertEqual(routine.weeks.first().days.count(), 1)

        # Representation check
        representation = RoutineSerializer(routine).data
        self.assertEqual(len(representation["weeks"][0]["days"]), 1)

    def test_update_exercise_serializer(self):
        # Data for updating the existing exercise
        update_data = {
            "exercise-name": "Updated Push-Up",
            "five-rep-max": 150,
            "default-weight": 60,
            "default-reps": 12,
        }

        # Initialize the serializer with the existing exercise instance and the new data
        serializer = ExerciseSerializer(self.exercise, data=update_data, partial=True)

        # Validate the data
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Save the updated instance
        updated_exercise = serializer.save()

        # Assertions to check if the exercise has been updated correctly
        self.assertEqual(updated_exercise.name, "Updated Push-Up")
        self.assertEqual(updated_exercise.five_rep_max, 150)
        self.assertEqual(updated_exercise.default_weight, 60)
        self.assertEqual(updated_exercise.default_reps, 12)

    def test_create_exercise_serializer(self):
        # Data for creating a new exercise
        new_exercise_data = {
            "name": "New Exercise",
            "five_rep_max": 100,
            "default_weight": 45,
            "default_reps": 15,
        }

        # Initialize the serializer with the new data
        serializer = ExerciseSerializer(data=new_exercise_data)

        # Validate the data
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Save the new instance, explicitly passing the user
        new_exercise = serializer.save(user=self.user)

        # Assertions to check if the new exercise has been created correctly
        self.assertEqual(new_exercise.name, "New Exercise")
        self.assertEqual(new_exercise.five_rep_max, 100)
        self.assertEqual(new_exercise.default_weight, 45)
        self.assertEqual(new_exercise.default_reps, 15)
        self.assertEqual(new_exercise.user, self.user)

    def test_routine_settings_serializer_update(self):
        routine_settings = RoutineSettings.objects.create(
            user=self.user, routine=self.routine
        )
        update_data = {"week_number": 2, "day_number": 3}
        serializer = RoutineSettingsSerializer(
            routine_settings, data=update_data, partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_settings = serializer.save()
        self.assertEqual(updated_settings.week_number, 2)
        self.assertEqual(updated_settings.day_number, 3)
