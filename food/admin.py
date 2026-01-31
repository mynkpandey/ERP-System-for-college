from django.contrib import admin
from .models import FoodItem, FoodOrder

admin.site.register(FoodItem)
admin.site.register(FoodOrder)
