from django.shortcuts import render, redirect
from .models import Attendance
from accounts.models import Student, Faculty


# ✅ Attendance Dashboard (Faculty One Click Marking)
def attendance_dashboard(request):

    students = Student.objects.all()

    # Ensure Faculty exists
    faculty = Faculty.objects.first()
    if not faculty:
        return render(request, "attendance/dashboard.html", {
            "records": [],
            "error": "⚠ Please add Faculty in Admin Panel first!"
        })

    # Create attendance records automatically
    for student in students:
        Attendance.objects.get_or_create(
            student=student,
            faculty=faculty
        )

    records = Attendance.objects.all()

    return render(request, "attendance/dashboard.html", {"records": records})


# ✅ Mark Student Present
def mark_present(request, id):
    record = Attendance.objects.get(id=id)
    record.status = True
    record.save()
    return redirect("attendance_dashboard")


# ✅ Mark Student Absent
def mark_absent(request, id):
    record = Attendance.objects.get(id=id)
    record.status = False
    record.save()
    return redirect("attendance_dashboard")


# ✅ Absentee Detection + Notification Simulation
def absentee_list(request):
    absentees = Attendance.objects.filter(status=False)

    # Simulated Notifications
    notifications = []
    for a in absentees:
        msg = f"Notification sent to Parent of {a.student.name} ({a.student.parent_email})"
        notifications.append(msg)

    return render(request, "attendance/absentees.html", {
        "absentees": absentees,
        "notifications": notifications
    })
