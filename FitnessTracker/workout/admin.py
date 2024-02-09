from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(Set)


class ExerciseLogInline(admin.TabularInline):
    model = Set
    extra = 3


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    inlines = [ExerciseLogInline]
