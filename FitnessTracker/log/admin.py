from django.contrib import admin
from .models import CardioLog, WeightLog, WorkoutLog, WorkoutSet, FoodLog, FoodItem

# Register your models here.
admin.site.register(CardioLog)
admin.site.register(WorkoutSet)
admin.site.register(WeightLog)
admin.site.register(FoodLog)
admin.site.register(FoodItem)


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 1


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    inlines = [WorkoutSetInline]
