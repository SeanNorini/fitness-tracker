# Generated by Django 4.2 on 2024-04-07 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='routinesettings',
            name='workout_number',
        ),
        migrations.AddField(
            model_name='routinesettings',
            name='workout_index',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]