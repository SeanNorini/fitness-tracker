from django.db import models
from users.models import User


# Create your models here.
class FoodLogEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="food_logs")
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        unique_together = ("user", "date")


class FoodItem(models.Model):
    log_entry = models.ForeignKey(
        FoodLogEntry, on_delete=models.CASCADE, related_name="food_items"
    )
    name = models.CharField(max_length=200)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    carbs = models.DecimalField(max_digits=5, decimal_places=2)
    fat = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
