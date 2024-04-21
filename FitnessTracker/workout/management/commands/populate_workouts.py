from django.core.management.base import BaseCommand
from users.models import User
from workout.models import Exercise, Workout
import random


class Command(BaseCommand):
    help = "Populates the database with a list of exercises"

    def handle(self, *args, **options):
        workout_names = self.get_workout_names()
        for _ in range(15):
            user = User.get_default_user()
            name = workout_names.pop(random.randint(0, len(workout_names) - 1))
            exercises = Command.get_random_exercises()
            workout = Workout.objects.create(user=user, name=name)
            workout.exercises.set(exercises)
            config = Command.get_random_workout_config(exercises)
            workout.config = config
            workout.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with workouts.")
        )

    @staticmethod
    def get_workout_names():
        workout_names = [
            "Total Body Burn",
            "Upper Body Strength",
            "Lower Body Blast",
            "Core Crunch",
            "Cardio Rush",
            "Flexibility Flow",
            "HIIT Intensity",
            "Power Lifting Session",
            "CrossFit Challenge",
            "Bootcamp Basics",
            "Yoga Retreat",
            "Pilates Core",
            "Kickboxing Power",
            "Strength and Conditioning",
            "Endurance Training",
            "Speed and Agility",
            "Circuit Training",
            "Aerobic Fitness",
            "Body Sculpting",
            "Mobility Moves",
            "Athletic Training",
            "Functional Fitness",
            "Bodyweight Basics",
            "Advanced Calisthenics",
            "Zumba Dance",
            "Spin Cycle",
            "Marathon Prep",
            "Triathlon Ready",
            "Sports Specific",
            "Recovery Session",
            "Dynamic Stretching",
            "Kettlebell Kombat",
            "Strongman Setup",
            "Weightlifting 101",
            "Full Body Detox",
            "Beach Body",
            "Winter Warrior",
            "Spring Into Fitness",
            "Summer Sizzle",
            "Autumn Activation",
        ]

        return workout_names

    @staticmethod
    def get_random_exercises():
        exercise_objs = list(Exercise.objects.all())
        exercises = random.sample(exercise_objs, random.randint(3, 5))
        return exercises

    @staticmethod
    def get_random_workout_config(exercises):
        config = []
        for exercise in exercises:
            number_of_sets = random.randint(1, 5)
            sets = []
            number_of_reps = random.randint(5, 15)
            for _ in range(number_of_sets):
                sets.append(
                    {"amount": 0, "modifier": "percentage", "reps": number_of_reps}
                )
            config.append(
                {
                    "name": exercise.name,
                    "pk": exercise.pk,
                    "five_rep_max": 0,
                    "sets": sets,
                }
            )
        return config
