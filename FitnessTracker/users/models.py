from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    gender = models.CharField(max_length=1, default="m")
    height = models.PositiveIntegerField(default=70)
    weight = models.PositiveIntegerField(default=160)
    age = models.PositiveIntegerField(default=30)
