from django.utils import timezone
from rest_framework import serializers
from .models import User, UserSettings
from log.serializers import WeightLogSerializer
from log.models import WeightLog


class UpdateUserAccountSettingsSerializer(serializers.ModelSerializer):
    confirm_email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "confirm_email",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id", "username")

    def validate_confirm_email(self, value):
        if value != self.initial_data.get("email"):
            raise serializers.ValidationError("Emails do not match")
        return value


class UpdateUserSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSettings
        fields = (
            "system_of_measurement",
            "gender",
            "height",
            "body_weight",
            "body_fat",
            "age",
        )

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # Get data for weight_log
        weight_log_data = {
            "body_weight": validated_data.get("body_weight", None),
            "body_fat": validated_data.get("body_fat", None),
            "user": self.context["request"].user,
            "date": timezone.localdate(),
        }

        # Fetch today's weight log if it exists
        existing_log = WeightLog.objects.filter(
            user=weight_log_data["user"], date=weight_log_data["date"]
        ).first()

        # Initialize the WeightLogSerializer with the existing instance
        weight_log_serializer = WeightLogSerializer(
            instance=existing_log, data=weight_log_data
        )

        # Validate and save the weight log
        if weight_log_serializer.is_valid(raise_exception=True):
            weight_log_serializer.save()

        return instance
