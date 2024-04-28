from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from datetime import timedelta, datetime, date
from workout.models import Exercise, Workout
from .models import CardioLog, WeightLog, WorkoutLog, WorkoutSet, FoodItem, FoodLog
from .validators import (
    validate_not_future_date,
    validate_not_more_than_5_years_ago,
    validate_duration_min,
    validate_duration_max,
)


class WorkoutSetSerializer(serializers.ModelSerializer):
    exercise = serializers.StringRelatedField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get("include_defaults"):
            data["default_weight"] = instance.exercise.default_weight
            data["default_reps"] = instance.exercise.default_reps
            data["id"] = instance.exercise.id
        return data

    class Meta:
        model = WorkoutSet
        fields = [
            "workout_log",
            "exercise",
            "weight",
            "reps",
        ]


class WorkoutLogSerializer(serializers.ModelSerializer):
    workout_sets = WorkoutSetSerializer(many=True, read_only=True)

    def to_internal_value(self, data):
        user = self.context["request"].user
        data["user"] = user
        data["workout"] = Workout.get_workout(
            user=user, workout_name=data.get("workout_name", None)
        )
        data["total_time"] = timedelta(seconds=int(data.get("total_time", 0)))
        if data.get("date", None) is not None:
            date_values = [int(value) for value in data.get("date").split("-")]
            data["date"] = timezone.make_aware(
                datetime(date_values[0], date_values[1], date_values[2]),
                timezone.get_default_timezone(),
            ).date()

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["workout_name"] = instance.workout.name
        exercises = {}

        for workout_set in data["workout_sets"]:
            exercise_name = workout_set["exercise"]
            if exercise_name not in exercises:
                exercises[exercise_name] = {
                    "reps": [],
                    "weights": [],
                }
                if self.context.get("include_defaults"):
                    exercises[exercise_name].update(
                        {
                            "default_weight": workout_set["default_weight"],
                            "default_reps": workout_set["default_reps"],
                            "id": workout_set["id"],
                        }
                    )

            exercises[exercise_name]["reps"].append(workout_set["reps"])
            exercises[exercise_name]["weights"].append(workout_set["weight"])

        data["exercises"] = exercises

        del data["workout_sets"]
        data["pk"] = instance.pk
        return data

    def create(self, validated_data):
        workout_log_data = self.extract_workout_log_data(validated_data)
        with transaction.atomic():
            workout_log = WorkoutLog.objects.create(**workout_log_data)
            self.handle_workout_sets_creation(
                workout_log, validated_data.get("workout_exercises", [])
            )
            self.validate_and_save(workout_log)
            return workout_log

    def update(self, instance, validated_data):
        with transaction.atomic():
            self.delete_workout_sets(instance)
            self.handle_workout_sets_creation(
                instance, validated_data.get("workout_exercises", [])
            )
            instance.total_time = validated_data.get("total_time")
            self.validate_and_save(instance)
        return instance

    def delete_workout_sets(self, instance):
        WorkoutSet.objects.filter(workout_log=instance).delete()

    def handle_workout_sets_creation(self, workout_log, workout_exercises):
        for exercise in workout_exercises:
            ((exercise_name, sets),) = exercise.items()
            exercise, _ = Exercise.objects.get_or_create(
                user=workout_log.user, name=exercise_name
            )
            self.create_workout_sets(workout_log, exercise, sets)

    def create_workout_sets(self, workout_log, exercise, sets):
        for rep, weight in zip(sets["reps"], sets["weights"]):
            workout_set = WorkoutSet(
                workout_log=workout_log,
                exercise=exercise,
                reps=rep,
                weight=weight,
            )
            workout_set.full_clean()
            workout_set.save()

    def validate_and_save(self, instance):
        try:
            instance.full_clean()
            instance.save()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def extract_workout_log_data(self, validated_data):
        return {
            "workout": validated_data.get("workout"),
            "user": validated_data.get("user"),
            "date": validated_data.get("date"),
            "total_time": validated_data.get("total_time"),
        }

    class Meta:
        model = WorkoutLog
        fields = ["workout", "user", "date", "total_time", "workout_sets"]


class CardioLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardioLog
        fields = "__all__"
        read_only_fields = ["user"]

    def validate_datetime(self, value):
        validate_not_future_date(value)
        validate_not_more_than_5_years_ago(value)

        return value

    def validate_duration(self, value):
        validate_duration_min(value)
        validate_duration_max(value)
        return value

    def validate_distance(self, value):
        validator_min = MinValueValidator(0)
        validator_max = MaxValueValidator(99.99)
        validator_min(value)
        validator_max(value)
        return value

    def to_internal_value(self, data):
        updated_data = (
            {"datetime": data.get("datetime")} if data.get("datetime") else {}
        )
        updated_data["duration"] = timedelta(seconds=int(data.get("duration", 0)))
        updated_data["distance"] = float(data.get("distance", 0))

        return super().to_internal_value(updated_data)


class WeightLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeightLog
        fields = "__all__"
        read_only_fields = ["user"]

    def to_internal_value(self, data):
        data_date = data.get("date")
        if not isinstance(data_date, datetime) and not isinstance(data_date, date):
            data["date"] = datetime.strptime(data_date, "%B %d, %Y").date()

        return data


class FoodItemSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        nutrients = ["calories", "protein", "carbs", "fat"]
        for nutrient in nutrients:
            try:
                if nutrient == "calories":
                    data[nutrient] = int(float(data.get(nutrient, 0)))
                else:
                    data[nutrient] = float(data.get(nutrient, 0))
            except ValueError:
                raise serializers.ValidationError(
                    {nutrient: f"Invalid input for {nutrient}, must be a number."}
                )

        data.pop("serving", None)
        return data

    class Meta:
        model = FoodItem
        fields = ["name", "calories", "protein", "carbs", "fat"]


class FoodLogSerializer(serializers.ModelSerializer):
    food_items = FoodItemSerializer(many=True)

    class Meta:
        model = FoodLog
        fields = ["date", "food_items"]

    def create(self, validated_data):
        food_items_data = validated_data.pop("food_items")
        food_log, created = FoodLog.objects.get_or_create(**validated_data)

        if not created:
            food_log.food_items.all().delete()

        for food_item_data in food_items_data:
            FoodItem.objects.create(log_entry=food_log, **food_item_data)

        return food_log

    def update(self, instance, validated_data):
        food_items_data = validated_data.pop("food_items")

        # Update the FoodLog instance
        instance.date = validated_data.get("date", instance.date)
        instance.save()

        # Remove all previous food items
        instance.food_items.all().delete()

        # Create new food item entries
        for food_item_data in food_items_data:
            FoodItem.objects.create(log_entry=instance, **food_item_data)

        return instance
