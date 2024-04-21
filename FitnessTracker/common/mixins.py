from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from users.models import UserSettings


class DefaultMixin(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_settings"] = UserSettings.get_user_settings(self.request.user.id)
        return context
