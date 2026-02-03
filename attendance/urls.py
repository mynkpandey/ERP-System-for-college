from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("stats/", views.dashboard_stats, name="dashboard_stats"),

    # Camera attendance
    path("mark/", views.mark_attendance, name="mark_attendance"),
    path("finalize/", views.finalize_hour, name="finalize_hour"),
    path("finalize/slot/", views.finalize_slot, name="finalize_slot"),
    path("self-check/", views.self_check, name="self_check"),
    path("upload/", views.upload_mark, name="upload_mark"),

    # Manual attendance dashboard
    path("faculty/", views.attendance_dashboard, name="attendance_dashboard"),
    path("faculty/present/<int:id>/", views.faculty_mark_present, name="faculty_mark_present"),
    path("faculty/absent/<int:id>/", views.faculty_mark_absent, name="faculty_mark_absent"),

    # Absentees list
    path("absentees/", views.absentee_list, name="absentee_list"),
    path("absentees.json", views.absentees_json, name="absentees_json"),
    path("admin-tools/", views.admin_tools, name="admin_tools"),
    path("reset-today/", views.reset_today_statuses, name="reset_today"),
]
