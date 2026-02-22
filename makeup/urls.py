from django.urls import path
from . import views

urlpatterns = [
    path("", views.enter_remedial_code, name="enter_remedial_code"),
    path("dashboard/", views.makeup_dashboard, name="makeup_dashboard"),
    path("add/", views.add_makeup_class, name="add_makeup_class"),
]
