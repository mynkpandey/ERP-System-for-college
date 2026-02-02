from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Camera attendance
    path("mark/", views.mark_attendance, name="mark_attendance"),
    path("finalize/", views.finalize_hour, name="finalize_hour"),
    path("finalize/slot/", views.finalize_slot, name="finalize_slot"),

    # Manual attendance dashboard
    path("faculty/", views.attendance_dashboard, name="attendance_dashboard"),

    # Absentees list
    path("absentees/", views.absentee_list, name="absentee_list"),
]
