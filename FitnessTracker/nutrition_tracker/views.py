from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .services import Nutritionix, FoodLogService
import json
from log.models import FoodLog, FoodItem


# Create your views here.


class NutritionTrackerView(LoginRequiredMixin, TemplateView):
    template_name = "nutrition_tracker/nutrition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        modules = ["workout", "cardio", "nutrition", "log", "stats", "settings"]
        context["modules"] = modules

        context["template_content"] = "nutrition_tracker/nutrition.html"

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "nutrition_tracker/nutrition.html", context)
        else:
            return render(request, "base/index.html", context)


class FetchNutritionSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = kwargs["query"].lower()
        data = Nutritionix.search(query)
        return Response(data=data, status=status.HTTP_200_OK)


class FetchItemDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        item_type = kwargs["item_type"]
        item_id = kwargs["item_id"]
        data = Nutritionix.get_item(item_type, item_id)
        return Response(data=data, status=status.HTTP_200_OK)


class FetchNutritionSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_summary = FoodLogService.get_user_food_summary(request.user)
        return Response(data=user_summary, status=status.HTTP_200_OK)
