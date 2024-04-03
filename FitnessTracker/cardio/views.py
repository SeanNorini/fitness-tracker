from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, FormView
from django.utils import timezone
from workout.forms import CardioLogForm
from workout.models import CardioLog
from matplotlib.ticker import MaxNLocator
from matplotlib import pyplot as plt
from io import BytesIO
import base64
import matplotlib
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

matplotlib.use("Agg")


def plot_graph(user, selected_range):
    dates, distances, paces = CardioLog.get_graph_values(user, selected_range)

    if dates is None or distances is None or paces is None:
        return None

    plt.bar(dates, distances)

    plt.xlabel("Date", color="#f5f5f5", fontsize=16)
    plt.ylabel("Distance", color="#f5f5f5", fontsize=16)

    plt.gcf().set_facecolor("#212121")
    plt.xticks(color="#f5f5f5", fontsize=14)
    plt.yticks(color="#f5f5f5", fontsize=14)

    ax = plt.gca()
    ax.set_facecolor("#212121")
    ax.xaxis.set_major_locator(MaxNLocator(10))
    ax.yaxis.set_major_locator(MaxNLocator(10))
    ax.tick_params(color="#f5f5f5")

    for spine in ax.spines.values():
        spine.set_edgecolor("#f5f5f5")

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format="png", transparent=True)
    plt.close()
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64


class GetCardioSummariesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        selected_range = kwargs.get("selected_range")
        current_range, previous_range, extended_range = get_date_range(selected_range)

        response_data = {
            "summaries": [
                CardioLog.get_summary_for_range(request.user, current_range),
                CardioLog.get_summary_for_range(request.user, previous_range),
                CardioLog.get_summary_for_range(request.user, extended_range),
            ],
            "graph": (
                plot_graph(request.user, extended_range)
                if selected_range == "week"
                else plot_graph(request.user, current_range)
            ),
        }

        return Response(response_data)


# Create your views here.
class CardioView(TemplateView):
    template_name = "cardio/cardio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
        context["modules"] = modules

        context["template_content"] = "cardio/cardio.html"

        today = datetime.now().date()
        context["latest"] = CardioLog.get_summary(self.request.user, [today, today])

        yesterday = today - timedelta(days=1)
        context["previous"] = CardioLog.get_summary(
            self.request.user, [yesterday, yesterday]
        )

        context["weekly"] = CardioLog.get_summary_for_range(
            self.request.user, get_current_week()
        )

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("fetch") == "True":
            return render(request, "cardio/cardio.html", context)
        else:
            return render(request, "base/index.html", context)


class SaveCardioSessionView(LoginRequiredMixin, FormView):
    form_class = CardioLogForm

    def form_valid(self, form):

        log = form.save(commit=False)
        log.user = self.request.user
        log.save()

        return JsonResponse({"success": True})

    def form_invalid(self, form):
        return JsonResponse({"success": True})


class GetCardioLogView(LoginRequiredMixin, View):
    pass


def get_graph_range(user, graph_range):
    match graph_range:
        case "week":
            return get_current_week()
        case "month":
            return get_current_month()
        case "year":
            return get_current_year()
        case "all_time":
            start = (
                CardioLog.objects.filter(user=user)
                .order_by("datetime")
                .first()
                .datetime.date()
            )
            end = timezone.now().date() + timedelta(days=1)
            return [start, end]


def get_current_week():
    weekday = timezone.now().weekday()
    days = weekday + 1 if weekday <= 5 else 0
    start_date = timezone.now().date() - timezone.timedelta(days=days)
    end_date = start_date + timezone.timedelta(days=6)
    return [start_date, end_date]


def get_previous_week():
    week = get_current_week()
    week = [week[0] - timedelta(days=7), week[1] - timedelta(days=7)]
    return week


def get_current_month():
    current_date = timezone.now().date()

    # Get the first day of the current month
    start_date = current_date.replace(day=1)

    # Get the last day of the current month
    if start_date.month == 12:
        end_date = start_date.replace(day=31)
    else:
        end_date = start_date.replace(
            month=start_date.month + 1, day=1
        ) - timezone.timedelta(days=1)

    return [start_date, end_date]


def get_current_year():
    current_date = timezone.now().date()
    start_date = current_date.replace(month=1, day=1)
    end_date = start_date.replace(month=12, day=31)

    return [start_date, end_date]


def get_date_range(selected_range):
    today = timezone.now().date()
    match selected_range:
        case "week":
            return get_date_range_week(today)
        case "month":
            return get_date_range_month(today)
        case "year":
            return get_date_range_year(today)


def get_date_range_week(today):
    # Returns date ranges for today, previous day, and current week for cardio summaries and graph.
    start_date = today - timezone.timedelta(days=(today.weekday() + 1) % 7)
    end_date = start_date + timezone.timedelta(days=6)

    current_range = [today, today]
    previous_range = [
        today - timezone.timedelta(days=1),
        today - timezone.timedelta(days=1),
    ]
    extended_range = [start_date, end_date]

    return current_range, previous_range, extended_range


def get_date_range_month(today):
    # Returns date ranges for current month, previous month, and 6 months for cardio summaries and graph.
    start_date = today.replace(day=1)
    if start_date.month == 12:
        end_date = start_date.replace(day=31)
    else:
        end_date = start_date.replace(month=start_date.month + 1) - timezone.timedelta(
            days=1
        )

    # Calculate previous month end first to simplify operation
    previous_end_date = start_date - timezone.timedelta(days=1)
    previous_start_date = previous_end_date.replace(day=1)

    extended_month = start_date.month - 5
    if extended_month > 0:
        extended_start_date = start_date.replace(month=extended_month)
    else:
        extended_month += 12
        extended_start_date = start_date.replace(
            year=start_date.year - 1, month=extended_month
        )

    current_range = [start_date, end_date]
    previous_range = [previous_start_date, previous_end_date]
    extended_range = [extended_start_date, end_date]

    return current_range, previous_range, extended_range


def get_date_range_year(today):
    start_date = today.replace(month=1, day=1)
    end_date = today.replace(month=12, day=31)

    previous_start_date = start_date.replace(year=start_date.year - 1)
    previous_end_date = end_date.replace(year=end_date.year - 1)

    extended_start_date = start_date.replace(year=start_date.year - 100)

    current_range = [start_date, end_date]
    previous_range = [previous_start_date, previous_end_date]
    extended_range = [extended_start_date, end_date]

    return current_range, previous_range, extended_range
