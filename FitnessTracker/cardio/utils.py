from django.utils import timezone


def get_time_from_duration(duration):
    # Converts total seconds to hours, minutes and seconds
    if duration <= 0:
        return 0, 0, 0
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)

    return hours, minutes, seconds


def format_duration(duration):
    # Returns a duration formatted to H'M'SS"
    hours, minutes, seconds = get_time_from_duration(duration)
    if hours < 0 or minutes < 0 or seconds < 0:
        return ValueError

    if hours > 0:
        return f"{hours}h {minutes:02}' {seconds:02}\""
    else:
        return f"{minutes}' {seconds:02}\""


def get_calories_burned(distance_unit, distance, body_weight):
    # Returns calories burned based on distance and body weight
    if distance < 0 or body_weight < 0:
        return ValueError

    if distance_unit == "mi":
        calories_burned = (distance * 0.57) * (body_weight * 2.2)
    else:
        calories_burned = (distance * 1.036) * body_weight
    return int(calories_burned)


def get_start_dates(today, selected_range):
    match selected_range:
        case "week":
            return get_start_dates_for_week(today)
        case "month":
            return get_start_dates_for_month(today)
        case "year":
            return get_start_dates_for_year(today)


def get_start_dates_for_week(today):
    """Returns date ranges for today, yesterday, and last 7 days for cardio summaries and graph."""
    start_date = today
    previous_start_date = today - timezone.timedelta(days=1)
    extended_start_date = today - timezone.timedelta(days=6)

    return {
        "start_date": start_date,
        "previous_start_date": previous_start_date,
        "extended_start_date": extended_start_date,
    }


def get_start_dates_for_month(today):
    """Returns date ranges for current month, previous month, and 6 months for cardio summaries and graph."""
    start_date = today - timezone.timedelta(days=30)
    previous_start_date = today - timezone.timedelta(days=60)
    extended_start_date = today - timezone.timedelta(days=180)

    return {
        "start_date": start_date,
        "previous_start_date": previous_start_date,
        "extended_start_date": extended_start_date,
    }


def get_start_dates_for_year(today):
    """Returns date ranges for current year, previous year, and all-time for cardio summaries and graph."""
    start_date = today - timezone.timedelta(days=365)
    previous_start_date = today - timezone.timedelta(days=730)
    extended_start_date = today.replace(year=today.year - 100)

    return {
        "start_date": start_date,
        "previous_start_date": previous_start_date,
        "extended_start_date": extended_start_date,
    }
