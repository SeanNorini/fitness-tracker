from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(WorkoutSet)


class WorkoutSetInline(admin.TabularInline):
    model = WorkoutSet
    extra = 1


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    inlines = [WorkoutSetInline]


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    inlines = [WorkoutExerciseInline]
