import json
from log.models import FoodLog
from datetime import timedelta
from matplotlib import pyplot as plt
import requests
from django.utils import timezone
from dotenv import load_dotenv
import os
from common.common_utils import Graph

load_dotenv()


class Nutritionix:
    APP_ID = os.environ.get("APP_ID")
    APP_KEY = os.environ.get("APP_KEY")
    HEADERS = {
        "Content-Type": "application/json",
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
    }

    @staticmethod
    def search(query):
        url = "https://trackapi.nutritionix.com/v2/search/instant/"
        params = {"query": query}
        response = requests.get(url, headers=Nutritionix.HEADERS, params=params)
        return response.json() if response.status_code == 200 else None

    @staticmethod
    def get_item(item_type, item_id):
        if item_type == "branded":
            url = "https://trackapi.nutritionix.com/v2/search/item/"
            params = {"nix_item_id": item_id}
        else:
            url = "https://trackapi.nutritionix.com/v2/natural/nutrients/"
            params = {"query": item_id}

        response = (
            requests.get(url, headers=Nutritionix.HEADERS, params=params)
            if item_type == "branded"
            else requests.post(
                url, headers=Nutritionix.HEADERS, data=json.dumps(params)
            )
        )
        return response.json() if response.status_code == 200 else None


class FoodLogService:

    @staticmethod
    def get_user_food_summary(user):
        bar_graph_data = {"dates": [], "Calories": []}
        logs = FoodLog.objects.filter(
            user=user,
            date__range=(timezone.now() - timedelta(days=6), timezone.now()),
        )
        if not logs:
            return {"bar_graph_data": bar_graph_data, "pie_chart_data": []}

        total_carbs = total_protein = total_fat = total_calories = 0

        for log in logs:
            daily_calories = sum(food.calories for food in log.food_items.all())
            total_calories += daily_calories
            total_protein += sum(food.protein for food in log.food_items.all())
            total_fat += sum(food.fat for food in log.food_items.all())
            total_carbs += sum(food.carbs for food in log.food_items.all())
            bar_graph_data["dates"].append(log.date)
            bar_graph_data["Calories"].append(daily_calories)

        num_logs = len(logs)
        user_summary = {
            "avg_protein": round(total_protein / num_logs, 1),
            "avg_carbs": round(total_carbs / num_logs, 1),
            "avg_calories": round(total_calories / num_logs),
            "avg_fat": round(total_fat / num_logs, 1),
            "pie_chart_data": [total_protein, total_carbs, total_fat],
            "bar_graph_data": bar_graph_data,
        }
        return user_summary
