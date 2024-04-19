from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime, date


def validate_not_future_date(value):
    if type(value) is datetime:
        if value > timezone.now():
            raise ValidationError("The date cannot be in the future.")
    elif type(value) is date:
        if value > timezone.now().date():
            raise ValidationError("The date cannot be in the future.")


def validate_not_more_than_5_years_ago(value):
    five_years_ago = timezone.now() - timedelta(days=5 * 365)
    if type(value) is datetime:
        if value < five_years_ago:
            raise ValidationError("The date cannot be more than 5 years ago.")
    elif type(value) is date:
        if value < five_years_ago.date():
            raise ValidationError("The date cannot be more than 5 years ago.")


def validate_duration_min(value):
    if value < timedelta(seconds=0):
        raise ValidationError("Duration must be greater than or equal to 0 seconds.")


def validate_duration_max(value):
    if value > timedelta(days=1):
        raise ValidationError("Duration must be less than or equal to 24 hours.")
