from django.urls import path
from . import views

urlpatterns = [
    path("", views.food_menu, name="food_menu"),
    path("success/", views.order_success, name="order_success"),
    path("peak/", views.peak_times, name="peak_times"),
]
