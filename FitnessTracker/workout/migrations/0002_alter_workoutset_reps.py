# Generated by Django 4.2 on 2024-02-24 21:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workout", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workoutset",
            name="reps",
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MaxValueValidator(100),
                    django.core.validators.MinValueValidator(0),
                ]
            ),
        ),
    ]
