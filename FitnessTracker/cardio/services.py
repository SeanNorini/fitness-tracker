from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from .models import CardioLog
from .utils import (
    format_duration,
    get_calories_burned,
    get_start_dates,
)


def get_cardio_log_averages(log, user):
    distance = log["total_distance"]
    duration = log["total_duration"]
    count = log["count"]

    # Get averages if logs exist else return zeroes
    if count > 0:
        log.update(
            {
                "average_distance": round(distance / count, 2),
                "average_duration": format_duration(duration / count),
                "calories_burned": int(
                    get_calories_burned(user.distance_unit, distance, user.body_weight)
                    / count
                ),
            }
        )

    else:
        log.update({"average_distance": 0, "average_duration": 0, "calories_burned": 0})

    # Get formatted pace if valid distance else N/A
    if distance > 0:
        log["pace"] = format_duration(duration / distance)
    else:
        log["pace"] = "N/A"
    return log


def get_cardio_log_summaries(user, selected_range=None):
    # Get start dates for each period in selected range
    today = timezone.now().astimezone(timezone.get_current_timezone()).date()
    start_dates = get_start_dates(today, selected_range)

    # Get cardio logs and group them by day
    grouped_cardio_logs = get_cardio_logs_grouped_by_day(
        user, start_dates["extended_start_date"], today
    )

    # Aggregate logs for each period and get graph data for selected range
    aggregated_logs, graph_data = aggregate_cardio_logs(
        grouped_cardio_logs, start_dates, selected_range
    )

    if selected_range == "week":
        add_start_end_dates_to_graph_data(
            graph_data, start_dates["extended_start_date"], today
        )
    else:
        add_start_end_dates_to_graph_data(
            graph_data,
            start_dates["start_date"],
            today,
        )

    return [get_cardio_log_averages(log, user) for log in aggregated_logs], graph_data


def add_start_end_dates_to_graph_data(graph_data, start, end):
    # Add start and end range if no log data
    if not graph_data["dates"]:
        graph_data.update({"dates": [start, end], "distances": [0, 0]})
        return

    # Add start and end range if data doesn't exist for those dates
    if graph_data["dates"][0] != start:
        graph_data["dates"].insert(0, start)
        graph_data["distances"].insert(0, 0)
    if graph_data["dates"][-1] != end:
        graph_data["dates"].append(end)
        graph_data["distances"].append(0)


def get_cardio_logs_grouped_by_day(user, start, end):
    # Get queryset of user logs for given range
    cardio_logs = CardioLog.objects.filter(
        user=user, datetime__date__range=[start, end]
    )

    # Group logs by day and sum the distance and duration for each day
    grouped_cardio_logs = (
        cardio_logs.annotate(day=TruncDay("datetime"))
        .values("day")
        .annotate(total_distance=Sum("distance"))
        .annotate(total_duration=Sum("duration"))
    ).order_by("day")

    return grouped_cardio_logs


def aggregate_cardio_logs(cardio_logs, start_dates, selected_range):
    current, previous, extended = (
        {"total_distance": 0, "total_duration": 0, "count": 0} for _ in range(3)
    )
    graph_data = {
        "dates": [],
        "distances": [],
    }

    # Update log dictionaries for each time period
    for log in cardio_logs:
        date = log["day"].date()
        if date >= start_dates["start_date"]:
            update_log_dict_and_graph_data(current, graph_data, log, True)
        # Only add all logs to graph data if selected range is week
        elif date >= start_dates["previous_start_date"]:
            update_log_dict_and_graph_data(
                previous, graph_data, log, selected_range == "week"
            )
        else:
            update_log_dict_and_graph_data(
                extended, graph_data, log, selected_range == "week"
            )

    # Add current and previous logs to extended log to complete aggregate
    extended["total_distance"] += current["total_distance"] + previous["total_distance"]
    extended["total_duration"] += current["total_duration"] + previous["total_duration"]
    extended["count"] += current["count"] + previous["count"]

    return [current, previous, extended], graph_data


def update_log_dict_and_graph_data(log_dict, graph_data, log, update_graph):
    log_dict["total_distance"] += log["total_distance"]
    log_dict["total_duration"] += (
        log["total_duration"].total_seconds()
        if isinstance(log["total_duration"], timedelta)
        else log["total_duration"]  # Used for final extended aggregate
    )
    log_dict["count"] += 1

    if update_graph and graph_data is not None:
        graph_data["dates"].append(log["day"].date())
        graph_data["distances"].append(log["total_distance"])
