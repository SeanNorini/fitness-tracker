from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.base import BaseTemplateView
from .services import get_cardio_log_summaries


class CardioTemplateView(BaseTemplateView):
    template_name = "base/index.html"
    fetch_template_name = "cardio/cardio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template_content"] = "cardio/cardio.html"
        return context


class CardioLogSummariesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        selected_range = kwargs.get("selected_range")

        cardio_log_summaries, graph = get_cardio_log_summaries(
            request.user, selected_range
        )

        data = {
            "summaries": cardio_log_summaries,
            "graph": graph,
        }

        return Response(data)
