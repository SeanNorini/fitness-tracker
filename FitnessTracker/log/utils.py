from calendar import HTMLCalendar, month_name


class Calendar(HTMLCalendar):
    def __init__(
        self,
        firstweekday=6,
        workout_logs=None,
        weight_logs=None,
        cardio_logs=None,
    ):
        super().__init__(firstweekday)
        self.workout_logs = workout_logs
        self.weight_logs = weight_logs
        self.cardio_logs = cardio_logs

    def formatday(self, day, weekday):
        workout_log = self.workout_logs.filter(date__day=day).first()
        weight_log = self.weight_logs.filter(date__day=day).first()
        cardio_log = self.cardio_logs.filter(datetime__day=day).first()

        if day == 0:
            day_format = (
                '<td class="noday">&nbsp;</td>'  # If day is 0, display an empty cell
            )
        else:
            day_format = f'<td class="{self.cssclasses[weekday]} day" data-day="{day}"><div>{day}</div>'
            if workout_log is not None:
                day_format += '<div><span class="material-symbols-outlined exercise-icon text-xl">exercise</span></div>'
            if weight_log is not None:
                day_format += (
                    f'<div><span class="material-symbols-outlined monitor_weight-icon text-xl">'
                    f"monitor_weight</span></div>"
                )
            if cardio_log is not None:
                day_format += (
                    f'<div><span class="material-symbols-outlined steps-icon text-xl">'
                    f"steps</span></div>"
                )

            day_format += "</td>"
        return day_format

    def formatmonth(self, year, month, withyear=True):
        # Get the calendar table with the month's days
        cal = super().formatmonth(year, month, withyear)

        # Add a CSS class to the table
        cal = cal.replace(
            '<table border="0" cellpadding="0" cellspacing="0" class="month">',
            '<table class="month">',
        )

        cal = cal.replace(
            f'class="month"',
            f"class='row row-justify-space-between row-align-center full-width month p-0_2'",
        )

        current_month = month_name[month]
        cal = cal.replace(
            f"{current_month} {year}",
            f'<div><span class="material-symbols-outlined hover border bg-tertiary text-xl" id="nav-prev">'
            f"navigate_before</span></div>"
            f'<div id="month-name" data-month={month} data-year={year}>{current_month} {year}</div>'
            f'<div><span class="material-symbols-outlined hover border bg-tertiary text-xl" id="nav-next">'
            f"navigate_next</span></div>",
        )

        return cal
