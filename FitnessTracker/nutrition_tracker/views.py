from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
from django.views.generic import TemplateView
from matplotlib.dates import DateFormatter
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
import json
from .models import *
from django.utils import timezone
from matplotlib.ticker import MaxNLocator
from matplotlib import pyplot as plt
from io import BytesIO
import base64

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

        if request.headers.get("fetch") == "True":
            return render(request, "nutrition_tracker/nutrition.html", context)
        else:
            return render(request, "base/index.html", context)


class FetchNutritionSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = kwargs["query"].lower()
        data = nutritionix_api_search(query)
        return Response(data=data, status=status.HTTP_200_OK)


class FetchItemDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        item_type = kwargs["item_type"]
        item_id = kwargs["item_id"]
        data = nutritionix_api_get_item(item_type, item_id)
        return Response(data=data, status=status.HTTP_200_OK)


class SaveFoodLogAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        date = request.data["date"]
        foods = json.loads(request.data["foods"])

        existing_log = FoodLogEntry.objects.filter(user=request.user, date=date).first()
        with transaction.atomic():
            if existing_log:
                existing_log.food_items.all().delete()
            else:
                existing_log = FoodLogEntry(user=request.user, date=date)

            existing_log.save()
            for food in foods["food_item"]:
                food_item = FoodItem(
                    log_entry=existing_log,
                    name=food["name"],
                    calories=int(float(food["calories"])),
                    protein=float(food["protein"]),
                    carbs=float(food["carbs"]),
                    fat=float(food["fat"]),
                )
                food_item.save()

        return Response(data={}, status=status.HTTP_200_OK)


class FetchNutritionSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logs = FoodLogEntry.objects.filter(
            user=request.user,
            date__range=(timezone.now() - timedelta(days=6), timezone.now()),
        )
        if logs:
            total_carbs = 0
            total_protein = 0
            total_fat = 0
            total_calories = 0
            num_logs = 0
            daily_calories_list = []
            for log in logs:
                num_logs += 1
                daily_calories = 0

                for food in log.food_items.all():
                    total_calories += food.calories
                    daily_calories += food.calories
                    total_protein += food.protein
                    total_fat += food.fat
                    total_carbs += food.carbs
                daily_calories_list.append((log.date, daily_calories))

            user_summary = {
                "avg_protein": total_protein / num_logs,
                "avg_carbs": total_carbs / num_logs,
                "avg_calories": total_calories // num_logs,
                "avg_fat": total_fat / num_logs,
                "pie_chart": pie_chart(total_protein, total_carbs, total_fat),
                "bar_chart": bar_chart(daily_calories_list),
            }

            return Response(data=user_summary, status=status.HTTP_200_OK)
        else:
            return Response(data={}, status=status.HTTP_200_OK)


def pie_chart(total_protein, total_carbs, total_fat):
    # Extracting data for the pie chart
    labels = ["Protein", "Carbs", "Fat"]
    sizes = [total_protein, total_carbs, total_fat]
    colors = ["#ff9999", "#66b3ff", "#99ff99"]  # Colors for each macronutrient

    # Creating the pie chart
    plt.figure(figsize=(6, 6))
    patches, texts, autotexts = plt.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
    )
    for text in texts:
        text.set_fontsize(20)
        text.set_color("white")

    for autotext in autotexts:
        autotext.set_fontsize(24)

    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
    # Saving the pie chart to a buffer
    buffer = BytesIO()
    plt.savefig(
        buffer, format="png", transparent=True, bbox_inches="tight", pad_inches=0.0
    )
    plt.close()
    buffer.seek(0)

    # Encoding the image buffer to base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64


def bar_chart(calories_list):
    plt.bar(*zip(*calories_list))
    plt.xlabel("Date", color="#f5f5f5")
    plt.ylabel("Calories", color="#f5f5f5")
    plt.title("Daily Calorie Intake", color="#f5f5f5")

    plt.gcf().set_facecolor("#212121")
    plt.xticks(color="#f5f5f5")
    plt.yticks(color="#f5f5f5")
    plt.tight_layout()
    ax = plt.gca()
    ax.set_facecolor("#212121")

    ax.tick_params(color="#f5f5f5")

    date_format = DateFormatter("%m/%d")
    plt.gca().xaxis.set_major_formatter(date_format)

    for spine in ax.spines.values():
        spine.set_edgecolor("#f5f5f5")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", transparent=True)
    plt.close()
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64


def nutritionix_api_search(query):
    nutritionix_app_id = "277db243"
    nutritionix_app_key = "195d096f132e7afdccecfa2677b986c4"

    # Corrected URL and Headers
    url = "https://trackapi.nutritionix.com/v2/search/instant/"
    headers = {
        "Content-Type": "application/json",
        "x-app-id": nutritionix_app_id,
        "x-app-key": nutritionix_app_key,
    }

    params = {"query": query}

    # Using GET method and passing query as a URL parameter
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(
            f"Failed to retrieve data. Status code: {response.status_code}, Response: {response.text}"
        )


def nutritionix_api_get_item(item_type, item_id):
    nutritionix_app_id = "277db243"
    nutritionix_app_key = "195d096f132e7afdccecfa2677b986c4"

    headers = {
        "Content-Type": "application/json",
        "x-app-id": nutritionix_app_id,
        "x-app-key": nutritionix_app_key,
    }

    if item_type == "branded":
        url = "https://trackapi.nutritionix.com/v2/search/item/"
        params = {"nix_item_id": item_id}
        response = requests.get(url, headers=headers, params=params)
    else:
        url = "https://trackapi.nutritionix.com/v2/natural/nutrients/"
        data = {"query": item_id}
        response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(
            f"Failed to retrieve data. Status code: {response.status_code}, Response: {response.text}"
        )
