from rest_framework import serializers
from .models import (
    Routine,
    Week,
    Day,
    Workout,
    RoutineSettings,
    DayWorkout,
    Exercise,
)


class DaySerializer(serializers.ModelSerializer):
    workouts = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Day
        fields = ["day_number", "workouts"]

    def create(self, validated_data):
        workouts_data = validated_data.pop("workouts", [])
        day, _ = Day.objects.get_or_create(**validated_data)
        user = self.context["request"].user

        # Clear existing DayWorkout instances for this day
        DayWorkout.objects.filter(day=day).delete()

        # Create new DayWorkout instances for each workout
        for i, workout_name in enumerate(workouts_data):
            workout, _ = Workout.objects.get_or_create(name=workout_name, user=user)
            DayWorkout.objects.create(day=day, workout=workout, order=i)
        return day

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Use DayWorkout to preserve order
        workouts = (
            DayWorkout.objects.filter(day=instance)
            .order_by("order")
            .select_related("workout")
        )
        representation["workouts"] = [dw.workout.name for dw in workouts]
        return representation


class WeekSerializer(serializers.ModelSerializer):
    days = DaySerializer(many=True)

    class Meta:
        model = Week
        fields = ["week_number", "days"]


class RoutineSerializer(serializers.ModelSerializer):
    weeks = WeekSerializer(many=True)

    class Meta:
        model = Routine
        fields = ["name", "weeks", "pk"]

    def create(self, validated_data):
        weeks_data = validated_data.pop("weeks")
        user = self.context["request"].user
        name = validated_data.get("name")
        routine, _ = Routine.objects.get_or_create(
            name=name, user=user, defaults=validated_data
        )
        for week_data in weeks_data:
            week_number = week_data.get("week_number")
            days_data = week_data.pop("days")
            week, _ = Week.objects.get_or_create(
                routine=routine, week_number=week_number
            )
            for day_data in days_data:
                workouts_data = day_data.pop("workouts")
                day_number = day_data.pop("day_number")
                day, _ = Day.objects.get_or_create(
                    week=week, day_number=day_number, defaults={**day_data}
                )
                DayWorkout.objects.filter(day=day).delete()
                for workout_name in workouts_data:
                    workout, _ = Workout.objects.get_or_create(
                        name=workout_name, user=self.context["request"].user
                    )
                    day.workouts.add(workout.id)
        return routine


class RoutineSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineSettings
        fields = [
            "routine",
            "week_number",
            "day_number",
            "workout_index",
            "last_completed",
        ]  # Include all updatable fields

    def update(self, instance, validated_data):
        if "routine" in validated_data:
            routine = validated_data.pop("routine")
            instance.routine = routine

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ExerciseSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        if "exercise-pk" in data:
            data["id"] = data.pop("exercise-pk")
        if "exercise-name" in data:
            data["name"] = data.pop("exercise-name")
        if "five-rep-max" in data:
            data["five_rep_max"] = data.pop("five-rep-max")
        if "default-weight" in data:
            data["default_weight"] = data.pop("default-weight")
        if "default-reps" in data:
            data["default_reps"] = data.pop("default-reps")
        return data

    class Meta:
        model = Exercise
        exclude = ("user",)


class WorkoutSerializer(serializers.ModelSerializer):

    class Meta:
        fields = "__all__"
        read_only_fields = ["user"]
        model = Workout
