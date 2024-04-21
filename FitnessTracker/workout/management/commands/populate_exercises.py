from django.core.management.base import BaseCommand

from users.models import User
from workout.models import Exercise


class Command(BaseCommand):
    help = "Populates the database with a list of exercises"

    def handle(self, *args, **options):
        exercises = [
            "Squat",
            "Bench Press",
            "Deadlift",
            "Overhead Press",
            "Barbell Row",
            "Pull-Up",
            "Leg Press",
            "Bicep Curl",
            "Tricep Extension",
            "Chest Fly",
            "Leg Curl",
            "Leg Extension",
            "Lateral Raise",
            "Shoulder Shrug",
            "Dumbbell Row",
            "Sit-Up",
            "Push-Up",
            "Plank",
            "Lunge",
            "Burpee",
            "Box Jump",
            "Bicycle Crunch",
            "Russian Twist",
            "Mountain Climber",
            "Kettlebell Swing",
            "Wall Sit",
            "Jump Rope",
            "Treadmill Running",
            "Stationary Biking",
            "Elliptical Trainer",
            "Stair Climbing",
            "Power Clean",
            "Hang Clean",
            "Front Squat",
            "Back Squat",
            "Sumo Deadlift",
            "Hip Thrust",
            "Calf Raise",
            "Pec Deck Machine",
            "Lat Pulldown",
            "Seated Row",
            "Face Pull",
            "Hammer Curl",
            "Skull Crusher",
            "Turkish Get-Up",
            "Farmer's Walk",
            "Deadlift High Pull",
            "High Knees",
            "Tuck Jump",
            "Bear Crawl",
            "V-Up",
            "Toe Touch",
            "Windshield Wiper",
            "Superman Exercise",
            "Dragon Flag",
            "Pistol Squat",
            "Nordic Hamstring Curl",
        ]
        user, _ = User.objects.get_or_create(username="default")
        for exercise_name in exercises:
            Exercise.objects.get_or_create(name=exercise_name, user=user)

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with exercises.")
        )
