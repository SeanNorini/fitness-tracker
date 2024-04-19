import json
from log.models import FoodLog
from datetime import timedelta
from matplotlib.dates import DateFormatter
from matplotlib import pyplot as plt
import requests
from django.utils import timezone
from io import BytesIO
import base64
from dotenv import load_dotenv
import os

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
        logs = FoodLog.objects.filter(
            user=user,
            date__range=(timezone.now() - timedelta(days=6), timezone.now()),
        )
        if not logs:
            return None

        total_carbs = total_protein = total_fat = total_calories = 0
        daily_calories_list = []

        for log in logs:
            daily_calories = sum(food.calories for food in log.food_items.all())
            total_calories += daily_calories
            total_protein += sum(food.protein for food in log.food_items.all())
            total_fat += sum(food.fat for food in log.food_items.all())
            total_carbs += sum(food.carbs for food in log.food_items.all())
            daily_calories_list.append((log.date, daily_calories))

        num_logs = len(logs)
        user_summary = {
            "avg_protein": round(total_protein / num_logs, 1),
            "avg_carbs": round(total_carbs / num_logs, 1),
            "avg_calories": round(total_calories / num_logs),
            "avg_fat": round(total_fat / num_logs, 1),
            "pie_chart": pie_chart(total_protein, total_carbs, total_fat),
            "bar_chart": bar_chart(daily_calories_list),
        }
        return user_summary


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
