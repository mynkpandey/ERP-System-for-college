import os
from io import BytesIO
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from attendance.models import Attendance


class Command(BaseCommand):
    help = "Finalize current hour attendance: export .xlsx and reset statuses to absent"

    def handle(self, *args, **options):
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
        except Exception:
            self.stderr.write("openpyxl not available, aborting export")
            return

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
        self.stdout.write(f"Exported: {path}")

        Attendance.objects.filter(date=date.today()).update(status=False, last_marked_at=None)
        self.stdout.write("Statuses reset to absent for today")
