from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from datetime import timedelta
from .models import CardioLog
from .validators import (
    validate_not_future_date,
    validate_not_more_than_5_years_ago,
    validate_duration_min,
    validate_duration_max,
)


class CardioLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardioLog
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}}

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
        updated_data = {"datetime": data.get("datetime")}

        duration_hours = int(data.get("duration-hours", 0))
        duration_minutes = int(data.get("duration-minutes", 0))
        duration_seconds = int(data.get("duration-seconds", 0))
        updated_data["duration"] = timedelta(
            hours=duration_hours, minutes=duration_minutes, seconds=duration_seconds
        )

        distance_integer = data.get("distance-integer", 0)
        distance_decimal = data.get("distance-decimal", 0)
        updated_data["distance"] = float(f"{distance_integer}.{distance_decimal}")
        return super().to_internal_value(updated_data)

    def create(self, validated_data):
        validated_data["user"] = self.context["user"]
        return super().create(validated_data)
