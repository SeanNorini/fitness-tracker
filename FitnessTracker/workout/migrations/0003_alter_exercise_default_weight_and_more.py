# Generated by Django 4.2 on 2024-04-14 10:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0002_rename_modifier_exercise_default_modifier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='default_weight',
            field=models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(1500), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='five_rep_max',
            field=models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(1500), django.core.validators.MinValueValidator(0)]),
        ),
    ]