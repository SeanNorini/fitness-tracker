from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from calendar import HTMLCalendar, month_name


# Create your views here.
class LogView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modules = ["workout", "cardio", "log", "stats", "settings"]
        context["modules"] = modules
        context["css_file"] = "log/css/log.css"
        return context

    def get(self, request, *args, **kwargs):
        year = 2024
        month = 2
        cal = LogHTMLCalendar()
        html_calendar = cal.formatmonth(year, month)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return HttpResponse(html_calendar)
        context = self.get_context_data(**kwargs)
        context["calendar"] = html_calendar
        return render(request, "base/index.html", context)


class LogHTMLCalendar(HTMLCalendar):
    def formatweekheader(self):
        header = "".join(
            self.formatweekday(i) for i in range(6, -1, -1)
        )  # Start with Sunday
        return '<tr class="weekdays">' + header + "</tr>"

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # If day is 0, display an empty cell
        else:
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatmonth(self, year, month, withyear=True):
        # Get the calendar table with the month's days
        cal = super().formatmonth(year, month, withyear)

        # Add a CSS class to the table
        cal = cal.replace(
            '<table border="0" cellpadding="0" cellspacing="0" class="month">',
            '<table class="calendar month">',
        )

        current_month = month_name[month]
        cal = cal.replace(
            f"{current_month} {year}",
            f'<div><span class="material-symbols-outlined">navigate_before</span></div><div>{current_month} \
            {year}</div><div><span class="material-symbols-outlined">navigate_next</span></div>',
        )

        return cal
