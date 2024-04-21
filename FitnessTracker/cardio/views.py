from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.common_utils import Graph
from .services import get_cardio_log_summaries


class CardioTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "cardio/cardio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["template_content"] = "cardio/cardio.html"
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "cardio/cardio.html", context)
        else:
            return render(request, "base/index.html", context)


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
