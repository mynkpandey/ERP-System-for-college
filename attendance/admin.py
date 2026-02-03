from django.contrib import admin
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, date
import os
import csv
from .models import Attendance


def export_current_hour(modeladmin, request, queryset):
    now = timezone.localtime()
    start = now.replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    qs = Attendance.objects.filter(
        status=True,
        last_marked_at__gte=start,
        last_marked_at__lt=end
    ).select_related("student", "faculty")
    try:
        import openpyxl
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = start.strftime("%H") + "00"
        ws.append(["Name", "Registration Number", "Marked At", "Faculty"])
        added = set()
        for rec in qs:
            reg = rec.student.reg_no
            if reg in added:
                continue
            added.add(reg)
            marked_at = rec.last_marked_at.astimezone(
                timezone.get_current_timezone()
            ).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
            faculty_name = rec.faculty.name if rec.faculty else ""
            ws.append([rec.student.name, reg, marked_at, faculty_name])
        exports_dir = os.path.join(settings.BASE_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"attendance_{start.date()}_{start.strftime('%H')}00.xlsx"
        path = os.path.join(exports_dir, filename)
        wb.save(path)
        modeladmin.message_user(request, f"Exported to {path}")
    except Exception:
        exports_dir = os.path.join(settings.BASE_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"attendance_{start.date()}_{start.strftime('%H')}00.csv"
        path = os.path.join(exports_dir, filename)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Registration Number", "Marked At", "Faculty"])
            added = set()
            for rec in qs:
                reg = rec.student.reg_no
                if reg in added:
                    continue
                added.add(reg)
                marked_at = rec.last_marked_at.astimezone(
                    timezone.get_current_timezone()
                ).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
                faculty_name = rec.faculty.name if rec.faculty else ""
                writer.writerow([rec.student.name, reg, marked_at, faculty_name])
        modeladmin.message_user(request, f"Exported to {path}")


def reset_today_statuses(modeladmin, request, queryset):
    Attendance.objects.filter(date=date.today()).update(status=False, last_marked_at=None)
    modeladmin.message_user(request, "Reset statuses to absent for today")


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "faculty", "date", "status", "last_marked_at")
    list_filter = ("date", "status", "faculty")
    search_fields = ("student__name", "student__reg_no", "faculty__name")
    actions = [export_current_hour, reset_today_statuses]


admin.site.register(Attendance, AttendanceAdmin)
