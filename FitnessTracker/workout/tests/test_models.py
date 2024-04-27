from django.test import TestCase, TransactionTestCase
from django.core.cache import cache
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from common.test_globals import CREATE_USER
from workout.models import (
    Exercise,
    Workout,
    WorkoutSettings,
    Routine,
    Week,
    Day,
    DayWorkout,
    RoutineSettings,
)
from users.models import User
from workout.serializers import WorkoutSerializer

MAX_NAME_LENGTH = 100


class TestExerciseModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**CREATE_USER)

    def test_name_not_null(self):
        with self.assertRaises(ValidationError):
            exercise = Exercise.objects.create(user=self.user)
            exercise.full_clean()

    def test_name_max_length(self):
        exercise = Exercise.objects.create(user=self.user, name="a" * MAX_NAME_LENGTH)
        exercise.full_clean()

        with self.assertRaises(ValidationError):
            exercise.name = "a" * (MAX_NAME_LENGTH + 1)
            exercise.full_clean()

    def test_user_not_null(self):
        with self.assertRaises(IntegrityError):
            exercise = Exercise.objects.create()

    def test_str_method(self):
        exercise = Exercise.objects.create(user=self.user, name="test")
        self.assertEqual(str(exercise), "Test")

    def test_exercise_creation(self):
        exercise = Exercise.objects.create(
            user=self.user,
            name="Deadlift",
            five_rep_max=400,
            default_weight=150,
            default_reps=5,
            default_modifier="exact",
        )
        self.assertEqual(exercise.name, "Deadlift")
        self.assertEqual(exercise.five_rep_max, 400)

    def test_string_representation(self):
        exercise = Exercise.objects.create(user=self.user, name="Bench Press")
        self.assertEqual(str(exercise), "Bench Press")

    def test_unique_together_constraint(self):
        Exercise.objects.create(user=self.user, name="Squat")
        with self.assertRaises(IntegrityError):
            Exercise.objects.create(user=self.user, name="Squat")

    def test_get_exercise_creates_new(self):
        exercise_name = "Pull Up"
        exercise = Exercise.get_exercise(user=self.user, exercise_name=exercise_name)
        self.assertEqual(exercise.name, "Pull Up")
        self.assertTrue(
            Exercise.objects.filter(user=self.user, name="Pull Up").exists()
        )

    def test_get_exercise_retrieves_existing(self):
        Exercise.objects.create(user=self.user, name="Lat Pulldown")
        exercise = Exercise.get_exercise(user=self.user, exercise_name=" lat pulldown ")
        self.assertEqual(exercise.name, "Lat Pulldown")

    def test_update_five_rep_max_successful(self):
        exercise = Exercise.objects.create(
            user=self.user, name="Leg Press", five_rep_max=180
        )
        updated = exercise.update_five_rep_max(weight=200, reps=10)
        self.assertTrue(updated)
        exercise.refresh_from_db()
        self.assertGreater(exercise.five_rep_max, 180)

    def test_update_five_rep_max_unsuccessful(self):
        exercise = Exercise.objects.create(
            user=self.user, name="Leg Curl", five_rep_max=200
        )
        updated = exercise.update_five_rep_max(weight=100, reps=5)
        self.assertFalse(updated)
        exercise.refresh_from_db()
        self.assertEqual(exercise.five_rep_max, 200)

    def test_save_method_title_cases_name(self):
        exercise = Exercise(user=self.user, name="calf raise")
        exercise.save()
        self.assertEqual(exercise.name, "Calf Raise")


class TestWorkoutModel(TestCase):

    def setUp(cls):
        cache.clear()
        cls.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@test.com"
        )
        cls.exercise1 = Exercise.objects.create(
            user=cls.user, name="Squat", five_rep_max=300
        )
        cls.exercise2 = Exercise.objects.create(
            user=cls.user, name="Bench Press", five_rep_max=200
        )
        cls.workout = Workout.objects.create(user=cls.user, name="Leg Day")
        cls.workout.exercises.add(cls.exercise1, cls.exercise2)
        cls.user = User.objects.get(username="testuser")

    def test_name_not_null(self):
        with self.assertRaises(ValidationError):
            workout = Workout.objects.create(user=self.user)
            workout.full_clean()

    def test_name_max_length(self):
        workout = Workout.objects.create(
            user=self.user, name="a" * MAX_NAME_LENGTH, config="test"
        )
        workout.full_clean()

        with self.assertRaises(ValidationError):
            workout.name = "a" * (MAX_NAME_LENGTH + 1)
            workout.full_clean()

    def test_user_not_null(self):
        with self.assertRaises(IntegrityError):
            workout = Workout.objects.create(name="a")

    def test_string_representation(self):
        self.assertEqual(str(self.workout), "Leg Day")

    def test_configure_workout(self):
        config = [
            {
                "id": 1,
                "name": "Squat",
                "five_rep_max": 300,
                "sets": [{"amount": 80, "reps": 10, "modifier": "percentage"}],
            },
            {
                "id": 2,
                "name": "Bench Press",
                "five_rep_max": 200,
                "sets": [{"amount": 50, "reps": 5, "modifier": "exact"}],
            },
        ]

        self.workout.config = config
        workout_config = WorkoutSerializer(
            instance=self.workout, context={"configure": True}
        ).data

        self.assertEqual("Squat", workout_config["exercises"][0]["name"])
        self.assertEqual("Bench Press", workout_config["exercises"][1]["name"])
        self.assertEqual(workout_config["exercises"][0]["sets"]["weights"][0], 240)
        self.assertEqual(workout_config["exercises"][1]["sets"]["weights"][0], 50)

    def test_unique_together_constraint(self):
        Workout.objects.create(user=self.user, name="Arm Day")
        with self.assertRaises(IntegrityError):
            Workout.objects.create(user=self.user, name="Arm Day")

    def test_get_workout(self):
        workout = Workout.get_workout(self.user, "Leg Day")
        self.assertEqual(workout.name, "Leg Day")
        self.assertEqual(workout.user, self.user)

        # # Test default/fallback workout creation
        default_workout = Workout.get_workout(self.user, "Cardio Day")
        self.assertEqual(default_workout.name, "Cardio Day")
        self.assertIsNotNone(default_workout)


class WorkoutSettingsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")

    def test_creation_of_workout_settings(self):
        settings = WorkoutSettings.objects.create(user=self.user)
        self.assertEqual(settings.user, self.user)
        self.assertFalse(settings.auto_update_five_rep_max)  # Default value check
        self.assertFalse(settings.show_rest_timer)  # Default value check
        self.assertFalse(settings.show_workout_timer)  # Default value check

    def test_verbose_name_plural(self):
        self.assertEqual(
            str(WorkoutSettings._meta.verbose_name_plural), "Workout Settings"
        )


class RoutineModelTest(TransactionTestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@test.com"
        )
        self.default_user = User.objects.create_user(
            username="default", password="defaultpass"
        )
        self.routine = Routine.objects.create(user=self.user, name="Leg Day")
        Routine.objects.create(user=self.default_user, name="Default Routine")

    def test_string_representation(self):
        self.assertEqual(str(self.routine), "Leg Day")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Routine.objects.create(user=self.user, name="Leg Day")

    def test_get_routines(self):
        user_routines = Routine.get_routines(self.user)
        self.assertEqual(len(user_routines), 2)
        self.assertIn("Leg Day", [routine.name for routine in user_routines])

    def test_get_weeks(self):
        week = Week.objects.create(routine=self.routine, week_number=1)
        weeks = self.routine.get_weeks()
        self.assertEqual(list(weeks), [week])


class WeekDayModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.routine = Routine.objects.create(user=cls.user, name="4 Week Strength")

        cls.week = Week.objects.create(routine=cls.routine, week_number=1)
        cls.day = Day.objects.create(week=cls.week, day_number=1)

        cls.workout = Workout.objects.create(user=cls.user, name="Upper Body Strength")

    def test_week_creation(self):
        self.assertEqual(self.week.week_number, 1)
        self.assertEqual(str(self.week), f"Week 1 of 4 Week Strength")

    def test_unique_week_per_routine(self):
        with self.assertRaises(Exception):
            Week.objects.create(routine=self.routine, week_number=1)

    def test_week_get_days(self):
        new_day = Day.objects.create(week=self.week, day_number=2)
        days = self.week.get_days()
        self.assertTrue(list(days), [self.day, new_day])

    def test_day_creation(self):
        self.assertEqual(self.day.day_number, 1)
        self.assertEqual(str(self.day), f"Day 1 of Week 1 of 4 Week Strength")

    def test_unique_day_per_week(self):
        with self.assertRaises(Exception):
            Day.objects.create(week=self.week, day_number=1)

    def test_day_get_workouts(self):
        DayWorkout.objects.create(day=self.day, workout=self.workout, order=1)
        workouts = self.day.get_workouts()
        self.assertEqual(list(workouts), [self.workout])

    def test_day_workout_creation_and_ordering(self):
        second_workout = Workout.objects.create(
            user=self.user, name="Lower Body Strength"
        )
        DayWorkout.objects.create(day=self.day, workout=self.workout, order=1)
        DayWorkout.objects.create(day=self.day, workout=second_workout, order=2)
        workouts = self.day.get_workouts()
        self.assertTrue(list(workouts)[0], self.workout)
        self.assertTrue(list(workouts)[1], second_workout)


class RoutineSettingsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")
        cls.routine = Routine.objects.create(user=cls.user, name="4 Week Program")
        cls.week = Week.objects.create(routine=cls.routine, week_number=1)
        cls.day = Day.objects.create(week=cls.week, day_number=1)
        cls.day2 = Day.objects.create(week=cls.week, day_number=2)
        cls.day3 = Day.objects.create(week=cls.week, day_number=3)
        cls.day4 = Day.objects.create(week=cls.week, day_number=4)
        cls.day5 = Day.objects.create(week=cls.week, day_number=5)
        cls.day6 = Day.objects.create(week=cls.week, day_number=6)
        cls.day7 = Day.objects.create(week=cls.week, day_number=7)
        cls.workout1 = Workout.objects.create(user=cls.user, name="Upper Body")
        cls.workout2 = Workout.objects.create(user=cls.user, name="Lower Body")
        DayWorkout.objects.create(day=cls.day, workout=cls.workout1, order=1)
        DayWorkout.objects.create(day=cls.day, workout=cls.workout2, order=2)
        cls.settings = RoutineSettings.objects.create(
            user=cls.user, routine=cls.routine
        )

    def test_get_next_workout(self):
        self.assertEqual(self.settings.workout_index, 0)
        workout = self.settings.get_next_workout()
        self.assertEqual(workout, self.workout2)
        self.assertEqual(self.settings.workout_index, 1)

    def test_get_prev_workout(self):
        self.settings.workout_index = 1
        self.settings.save()

        workout = self.settings.get_previous_workout()
        self.assertEqual(workout, self.workout1)
        self.assertEqual(self.settings.workout_index, 0)

    def test_boundary_next_workout(self):
        self.settings.workout_index = 1
        self.settings.get_next_workout()
        self.assertEqual(self.settings.workout_index, 0)
        self.assertEqual(self.settings.day_number, 2)

    def test_boundary_prev_workout(self):
        self.settings.workout_index = 0
        self.settings.get_previous_workout()
        self.assertEqual(self.settings.workout_index, 1)
        self.assertEqual(self.settings.day_number, 7)

    def test_no_workouts_available(self):
        DayWorkout.objects.all().delete()
        self.assertIsNone(self.settings.get_next_workout())
