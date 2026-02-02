from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
from io import BytesIO
from django.conf import settings

from .models import Attendance

from accounts.models import Student, Faculty



def dashboard(request):
    students = Student.objects.all()
    for s in students:
        Attendance.objects.get_or_create(student=s, date=date.today())
    records = Attendance.objects.filter(date=date.today())
    return render(request, "attendance/dashboard.html", {"records": records, "class_slots": getattr(settings, "CLASS_SLOTS", [])})


def mark_attendance(request):
    try:
        from .utils import mark_attendance_camera
        result = mark_attendance_camera()
        if isinstance(result, tuple):
            success, msg = result
            if success:
                messages.success(request, msg)
            else:
                messages.error(request, msg or "Unable to mark attendance")
        else:
            messages.error(request, "Unable to mark attendance")
    except Exception:
        messages.error(request, "Error using camera to mark attendance")
    return redirect("dashboard")


# ✅ Attendance Dashboard (Faculty One Click Marking)
def attendance_dashboard(request):
    students = Student.objects.all()

    faculty = Faculty.objects.first()
    if not faculty:
        return render(request, "attendance/dashboard.html", {
            "records": [],
            "error": "⚠ Please add Faculty in Admin Panel first!"
        })

    # Create today's attendance records if not exist
    for student in students:
        Attendance.objects.get_or_create(
            student=student,
            faculty=faculty,
            date=date.today()
        )

    records = Attendance.objects.filter(date=date.today())

    return render(request, "attendance/dashboard.html", {"records": records})



def finalize_hour(request):
    now = timezone.localtime()
    start = now.replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    present_records = Attendance.objects.filter(
        status=True,
        last_marked_at__gte=start,
        last_marked_at__lt=end
    ).select_related("student")
    try:
        import openpyxl
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = start.strftime("%H") + "00"
        ws.append(["Name", "Registration Number", "Marked At", "Faculty"])
        added = set()
        for rec in present_records:
            key = rec.student.reg_no
            if key in added:
                continue
            added.add(key)
            marked_at = rec.last_marked_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
            faculty_name = rec.faculty.name if rec.faculty else ""
            ws.append([rec.student.name, rec.student.reg_no, marked_at, faculty_name])
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        response = HttpResponse(
            stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"attendance_{start.date()}_{start.strftime('%H')}00.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
    except Exception:
        response = HttpResponse(content_type="text/csv")
        filename = f"attendance_{start.date()}_{start.strftime('%H')}00.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Registration Number"])
        added = set()
        for rec in present_records:
            key = rec.student.reg_no
            if key in added:
                continue
            added.add(key)
            writer.writerow([rec.student.name, rec.student.reg_no])
    Attendance.objects.filter(date=date.today()).update(status=False, last_marked_at=None)
    return response


def finalize_slot(request):
    slot_str = request.GET.get("slot")
    now = timezone.localtime()
    if not slot_str or "-" not in slot_str:
        start = now.replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
    else:
        parts = slot_str.split("-")
        h, m = parts[0].split(":")
        start = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
        hh, mm = parts[1].split(":")
        end = now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
    present_records = Attendance.objects.filter(
        status=True,
        last_marked_at__gte=start,
        last_marked_at__lt=end
    ).select_related("student", "faculty")
    try:
        import openpyxl
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = f"{start.strftime('%H%M')}-{end.strftime('%H%M')}"
        ws.append(["Name", "Registration Number", "Marked At", "Faculty"])
        added = set()
        for rec in present_records:
            key = rec.student.reg_no
            if key in added:
                continue
            added.add(key)
            marked_at = rec.last_marked_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
            faculty_name = rec.faculty.name if rec.faculty else ""
            ws.append([rec.student.name, rec.student.reg_no, marked_at, faculty_name])
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        response = HttpResponse(
            stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"attendance_{start.date()}_{start.strftime('%H%M')}-{end.strftime('%H%M')}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
    except Exception:
        response = HttpResponse(content_type="text/csv")
        filename = f"attendance_{start.date()}_{start.strftime('%H%M')}-{end.strftime('%H%M')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Registration Number", "Marked At", "Faculty"])
        added = set()
        for rec in present_records:
            key = rec.student.reg_no
            if key in added:
                continue
            added.add(key)
            marked_at = rec.last_marked_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
            faculty_name = rec.faculty.name if rec.faculty else ""
            writer.writerow([rec.student.name, rec.student.reg_no, marked_at, faculty_name])
    Attendance.objects.filter(date=date.today()).update(status=False, last_marked_at=None)
    return response
 


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
