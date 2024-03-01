# Generated by Django 4.2 on 2024-02-29 20:45

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_remove_user_age_remove_user_gender_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserBodyCompositionSettings",
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
                (
                    "unit_of_measurement",
                    models.CharField(
                        choices=[("Imperial", "Imperial"), ("Metric", "Metric")],
                        default="Imperial",
                        max_length=8,
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female")],
                        default="M",
                        max_length=1,
                    ),
                ),
                (
                    "height",
                    models.FloatField(
                        default=70,
                        validators=[
                            django.core.validators.MinValueValidator(20.0),
                            django.core.validators.MaxValueValidator(270.0),
                        ],
                    ),
                ),
                (
                    "weight",
                    models.FloatField(
                        default=160,
                        validators=[
                            django.core.validators.MinValueValidator(30.0),
                            django.core.validators.MaxValueValidator(1000.0),
                        ],
                    ),
                ),
                (
                    "bodyfat",
                    models.FloatField(
                        default=20,
                        validators=[
                            django.core.validators.MinValueValidator(5.0),
                            django.core.validators.MaxValueValidator(60.0),
                        ],
                    ),
                ),
                (
                    "age",
                    models.PositiveIntegerField(
                        default=30,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(120),
                        ],
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="weightlog",
            name="bodyfat",
            field=models.FloatField(
                default=20,
                validators=[
                    django.core.validators.MinValueValidator(5.0),
                    django.core.validators.MaxValueValidator(60.0),
                ],
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="weightlog",
            name="weight",
            field=models.FloatField(
                validators=[
                    django.core.validators.MinValueValidator(30.0),
                    django.core.validators.MaxValueValidator(1000.0),
                ]
            ),
        ),
        migrations.DeleteModel(
            name="UserSettings",
        ),
    ]