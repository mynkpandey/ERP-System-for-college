from django.contrib import admin
from .models import FoodItem, FoodOrder


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)


class FoodOrderAdmin(admin.ModelAdmin):
    list_display = ("student", "item", "time_slot", "ordered_at")
    list_filter = ("time_slot", "ordered_at")
    search_fields = ("student__name", "student__reg_no", "item__name")


admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(FoodOrder, FoodOrderAdmin)
