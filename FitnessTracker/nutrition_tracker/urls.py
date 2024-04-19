from django.urls import path
from . import views

urlpatterns = [
    path("", views.NutritionTrackerView.as_view(), name="nutrition_tracker"),
    path(
        "get_search_results/<str:query>",
        views.FetchNutritionSearchAPIView.as_view(),
        name="get_search_results",
    ),
    path(
        "get_item_details/<str:item_type>/<str:item_id>",
        views.FetchItemDetailsAPIView.as_view(),
        name="get_item_details",
    ),
    path(
        "get_nutrition_summary/<str:period>/",
        views.FetchNutritionSummaryAPIView.as_view(),
        name="get_nutrition_summary",
    ),
]
