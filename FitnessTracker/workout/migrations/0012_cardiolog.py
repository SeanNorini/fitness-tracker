# Generated by Django 5.0.2 on 2024-03-23 08:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workout", "0011_alter_exercise_unique_together_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CardioLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                (
                    "duration_hours",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(24)],
                    ),
                ),
                (
                    "duration_minutes",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(59)],
                    ),
                ),
                (
                    "duration_seconds",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(59)],
                    ),
                ),
                (
                    "distance",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=4,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(99.99),
                        ],
                    ),
                ),
            ],
        ),
    ]
