from log.models import WeightLog, WorkoutSet
from workout.models import Exercise
from django.db.models import Max
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from common.common_utils import Graph


def get_exercise_graph_data(graph_data, exercise_name, user, start, end):
    exercise = Exercise.objects.filter(name=exercise_name, user=user).first()
    max_weight_info = (
        WorkoutSet.objects.filter(
            exercise=exercise,
            workout_log__date__range=[start, end],
        )
        .values("workout_log__date")
        .annotate(max_weight=Max("weight"))
        .order_by("workout_log__date")
    )

    for entry in max_weight_info:
        graph_data["dates"].append(entry["workout_log__date"])
        graph_data["Weight"].append(entry["max_weight"])
    # exercise_values = list(workout_sets.values_list("weight", flat=True))
    return graph_data


def get_body_weight_graph_data(graph_data, user, start, end):
    weight_info = WeightLog.objects.filter(user=user, date__range=[start, end]).values(
        "date", "body_weight"
    )
    for entry in weight_info:
        graph_data["dates"].append(entry["date"])
        graph_data["Weight"].append(entry["body_weight"])

    return graph_data


def get_graph_data(user, stat, start, end):
    graph_data = {"dates": [], "Weight": []}
    if stat == "body-weight":
        return get_body_weight_graph_data(graph_data, user, start, end)
    else:
        return get_exercise_graph_data(graph_data, stat, user, start, end)


def get_graph(user, stat, months):
    start = timezone.localdate() - relativedelta(months=months)
    end = timezone.localdate()
    graph_data = get_graph_data(user, stat, start, end)
    return Graph(graph_data, "Weight", "line").plot_graph()
