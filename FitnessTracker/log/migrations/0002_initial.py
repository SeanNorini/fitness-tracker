# Generated by Django 4.2 on 2024-04-19 04:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("workout", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("log", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="workoutset",
            name="exercise",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="workout.exercise"
            ),
        ),
        migrations.AddField(
            model_name="workoutset",
            name="workout_log",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="workout_sets",
                to="log.workoutlog",
            ),
        ),
        migrations.AddField(
            model_name="workoutlog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="workoutlog",
            name="workout",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="workout.workout"
            ),
        ),
        migrations.AddField(
            model_name="weightlog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="foodlog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="food_logs",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="fooditem",
            name="log_entry",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="food_items",
                to="log.foodlog",
            ),
        ),
        migrations.AddField(
            model_name="cardiolog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterUniqueTogether(
            name="weightlog",
            unique_together={("user", "date")},
        ),
        migrations.AlterUniqueTogether(
            name="foodlog",
            unique_together={("user", "date")},
        ),
    ]
