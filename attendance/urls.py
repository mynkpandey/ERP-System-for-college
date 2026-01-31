from django.urls import path
from . import views

urlpatterns = [
    path("", views.attendance_dashboard, name="attendance_dashboard"),

    path("present/<int:id>/", views.mark_present, name="mark_present"),
    path("absent/<int:id>/", views.mark_absent, name="mark_absent"),

    path("absentees/", views.absentee_list, name="absentees"),
]
