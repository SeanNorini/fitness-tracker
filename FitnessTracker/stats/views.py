from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stats.services import get_graph
from workout.base import ExerciseTemplateView


# Create your views here.
class StatsView(ExerciseTemplateView):
    template_name = "base/index.html"
    fetch_template_name = "workout/stats.html"


class StatsGraphAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        months = int(kwargs.get("range"))
        stat = kwargs.get("stat")

        graph = get_graph(request.user, stat, months)

        return Response(data={"graph": graph})
