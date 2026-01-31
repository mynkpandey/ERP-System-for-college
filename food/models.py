from django.db import models
from accounts.models import Student


# ✅ Food Item Model (Menu)
class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


# ✅ Order Model (Pre-Order System)
class FoodOrder(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)

    time_slot = models.CharField(
        max_length=50,
        choices=[
            ("10:30 AM", "10:30 AM"),
            ("12:30 PM", "12:30 PM"),
            ("02:30 PM", "02:30 PM"),
            ("04:30 PM", "04:30 PM"),
        ]
    )

    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} ordered {self.item.name} at {self.time_slot}"
