from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(WorkoutSet)
admin.site.register(CardioLog)
admin.site.register(Week)
admin.site.register(Routine)
admin.site.register(Day)


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 1


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    inlines = [WorkoutSetInline]
