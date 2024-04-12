from django.shortcuts import render
from django.views.generic import TemplateView
from .serializers import CardioLogSerializer
from .services import get_cardio_log_summaries
from matplotlib.ticker import MaxNLocator
from matplotlib import pyplot as plt
from io import BytesIO
import base64
import matplotlib
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import pandas as pd

matplotlib.use("Agg")


def plot_graph(graph_data):

    df = pd.DataFrame(
        {
            "Date": graph_data["dates"],
            "Distance": graph_data["distances"],
        }
    )

    # Set 'Date' as the index
    df.set_index("Date", inplace=True)

    start_date = df.index.min()
    end_date = df.index.max()
    full_date_range = pd.date_range(start=start_date, end=end_date)

    # Reindex your DataFrame to include all dates in the range, filling missing ones with 0
    df_full = df.reindex(full_date_range, fill_value=0)

    # Plotting
    plt.figure(figsize=(10, 6))
    df_full["Distance"].plot(kind="bar", width=0.8, color="skyblue")

    plt.ylabel("Distance", color="#f5f5f5", fontsize=24)

    plt.gcf().set_facecolor("#212121")

    ax = plt.gca()
    ax.set_facecolor("#212121")

    ax.set_xticklabels(
        [date.strftime("%m/%d") for date in df_full.index],
        rotation=45,
        color="#f5f5f5",
        fontsize=24,
    )

    if max(df_full["Distance"]) == 0:
        ax.set_ylim(0, 5)

    if len(df_full) > 7:
        ax.xaxis.set_major_locator(MaxNLocator(10))
        ax.yaxis.set_major_locator(MaxNLocator(10))
    plt.yticks(color="#f5f5f5", fontsize=14)
    ax.tick_params(colors="#f5f5f5")
    for spine in ax.spines.values():
        spine.set_edgecolor("#f5f5f5")

    plt.tight_layout()

    # Save to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", transparent=True)
    plt.close()
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64


class CardioView(TemplateView):
    template_name = "cardio/cardio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
        context["modules"] = modules

        context["template_content"] = "cardio/cardio.html"

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "cardio/cardio.html", context)
        else:
            return render(request, "base/index.html", context)


class GetCardioLogSummariesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        selected_range = kwargs.get("selected_range")

        cardio_log_summaries, graph_data = get_cardio_log_summaries(
            request.user, selected_range
        )

        data = {
            "summaries": cardio_log_summaries,
            "graph": (plot_graph(graph_data)),
        }

        return Response(data)


class CreateCardioLogAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CardioLogSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}
