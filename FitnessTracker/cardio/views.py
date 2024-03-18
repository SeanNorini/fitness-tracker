from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


# Create your views here.
class CardioView(TemplateView):
    template_name = "cardio/cardio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        modules = ["workout", "cardio", "log", "stats", "settings"]
        context["modules"] = modules

        context["template_content"] = "cardio/cardio.html"

        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("Fetch") == "True":
            return render(
                request,
                "cardio/cardio.html",
            )
        else:
            return render(request, "base/index.html", self.get_context_data(**kwargs))
