# Generated by Django 4.2 on 2024-04-20 07:05

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="modules",
            field=models.JSONField(default=users.models.default_modules),
        ),
    ]
