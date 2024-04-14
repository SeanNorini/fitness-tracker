# Generated by Django 4.2 on 2024-04-12 20:07

import datetime
import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import log.models
import log.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CardioLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(validators=[log.validators.validate_not_future_date, log.validators.validate_not_more_than_5_years_ago])),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=1800), validators=[log.validators.validate_duration_min, log.validators.validate_duration_max])),
                ('distance', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99.99)])),
            ],
        ),
        migrations.CreateModel(
            name='WeightLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body_weight', models.FloatField(validators=[django.core.validators.MinValueValidator(30.0), django.core.validators.MaxValueValidator(1000.0)])),
                ('body_fat', models.FloatField(validators=[django.core.validators.MinValueValidator(5.0), django.core.validators.MaxValueValidator(60.0)])),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, validators=[log.models.validate_date])),
                ('total_time', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MaxValueValidator(1500.0), django.core.validators.MinValueValidator(0.0)])),
                ('reps', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
            ],
        ),
    ]
