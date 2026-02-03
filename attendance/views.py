from django.shortcuts import render, redirect
from datetime import date
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
import csv
from io import BytesIO
from django.conf import settings
from django.shortcuts import render
import os

from .models import Attendance

from accounts.models import Student, Faculty



def dashboard(request):
    students = Student.objects.all()
    today = date.today()
    
    # Get existing records first
    existing_records = Attendance.objects.filter(date=today)
    existing_student_ids = set(existing_records.values_list('student_id', flat=True))
    
    # Create only missing records
    for student in students:
        if student.id not in existing_student_ids:
            try:
                Attendance.objects.create(student=student, date=today)
            except:
                # If record already exists (race condition), just continue
                pass
    
    records = Attendance.objects.filter(date=today)

    # Metrics: present/absent counts for today
    present_count = records.filter(status=True).count()
    absent_count = records.filter(status=False).count()

    # Slot-based attendance percentage (current hour by default or ?slot=HH:MM-HH:MM)
    slot_str = request.GET.get("slot")
    now = timezone.localtime()
    if slot_str and "-" in slot_str:
        try:
            start_hm, end_hm = slot_str.split("-")
            sh, sm = start_hm.split(":")
            eh, em = end_hm.split(":")
            slot_start = now.replace(hour=int(sh), minute=int(sm), second=0, microsecond=0)
            slot_end = now.replace(hour=int(eh), minute=int(em), second=0, microsecond=0)
        except Exception:
            slot_start = now.replace(minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(hours=1)
    else:
        slot_start = now.replace(minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(hours=1)

    present_in_slot = Attendance.objects.filter(
        status=True,
        last_marked_at__gte=slot_start,
        last_marked_at__lt=slot_end
    ).count()
    total_students = records.count()
    attendance_percentage = round((present_in_slot / total_students) * 100) if total_students else 0

    return render(
        request,
        "attendance/dashboard.html",
        {
            "records": records,
            "class_slots": getattr(settings, "CLASS_SLOTS", []),
            "present_count": present_count,
            "absent_count": absent_count,
            "attendance_percentage": attendance_percentage,
        },
    )


def dashboard_stats(request):
    today = date.today()
    records = Attendance.objects.filter(date=today)
    present_count = records.filter(status=True).count()
    absent_count = records.filter(status=False).count()
    slot_str = request.GET.get("slot")
    now = timezone.localtime()
    if slot_str and "-" in slot_str:
        try:
            start_hm, end_hm = slot_str.split("-")
            sh, sm = start_hm.split(":")
            eh, em = end_hm.split(":")
            slot_start = now.replace(hour=int(sh), minute=int(sm), second=0, microsecond=0)
            slot_end = now.replace(hour=int(eh), minute=int(em), second=0, microsecond=0)
        except Exception:
            slot_start = now.replace(minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(hours=1)
    else:
        slot_start = now.replace(minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(hours=1)
    present_in_slot = Attendance.objects.filter(
        status=True,
        last_marked_at__gte=slot_start,
        last_marked_at__lt=slot_end
    ).count()
    total_students = records.count()
    attendance_percentage = round((present_in_slot / total_students) * 100) if total_students else 0
    payload_records = []
    for rec in records:
        lm = rec.last_marked_at
        lm_disp = timezone.localtime(lm).strftime("%H:%M:%S") if lm else None
        payload_records.append({"id": rec.id, "status": rec.status, "last_marked_at": lm.isoformat() if lm else None, "last_marked_at_display": lm_disp})
    return JsonResponse({
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_percentage": attendance_percentage,
        "records": payload_records,
    })


def absentees_json(request):
    today = date.today()
    absentees = Attendance.objects.filter(date=today, status=False).select_related("student")
    items = [{"name": a.student.name, "email": a.student.parent_email} for a in absentees]
    return JsonResponse({"absentees": items})


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
    today = date.today()

    faculty = Faculty.objects.first()
    if not faculty:
        return render(request, "attendance/faculty.html", {
            "records": [],
            "error": "⚠ Please add Faculty in Admin Panel first!"
        })

    # Get existing records first
    existing_records = Attendance.objects.filter(date=today)
    existing_student_ids = set(existing_records.values_list('student_id', flat=True))
    
    # Create only missing records
    for student in students:
        if student.id not in existing_student_ids:
            try:
                Attendance.objects.create(
                    student=student,
                    faculty=faculty,
                    date=today
                )
            except:
                # If record already exists (race condition), just continue
                pass

    records = Attendance.objects.filter(date=today)

    present_count = records.filter(status=True).count()
    absent_count = records.filter(status=False).count()
    total_count = records.count()
    attendance_percentage = round((present_count / total_count) * 100) if total_count else 0

    return render(request, "attendance/faculty.html", {
        "records": records,
        "present_count": present_count,
        "absent_count": absent_count,
        "total_count": total_count,
        "attendance_percentage": attendance_percentage,
    })



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
    if not present_records.exists():
        present_records = Attendance.objects.filter(
            date=date.today(),
            status=True
        ).select_related("student", "faculty")
    try:
        import openpyxl
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = f"{start.strftime('%H%M')}-{end.strftime('%H%M')}"
        ws.append(["Registration Number", "Name", "Marked At", "Faculty"])
        added = set()
        for rec in present_records:
            key = rec.student.reg_no
            if key in added:
                continue
            added.add(key)
            marked_at = rec.last_marked_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
            faculty_name = rec.faculty.name if rec.faculty else ""
            ws.append([rec.student.reg_no, rec.student.name, marked_at, faculty_name])
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
        writer.writerow(["Registration Number", "Name", "Marked At", "Faculty"])
        added = set()
        for rec in present_records:
            key = rec.student.reg_no
            if key in added:
                continue
            added.add(key)
            marked_at = rec.last_marked_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if rec.last_marked_at else ""
            faculty_name = rec.faculty.name if rec.faculty else ""
            writer.writerow([rec.student.reg_no, rec.student.name, marked_at, faculty_name])
    Attendance.objects.filter(date=date.today()).update(status=False, last_marked_at=None)
    return response


def self_check(request):
    libs_status = "ok"
    camera_status = "unavailable"
    total_students = Student.objects.count()
    with_images = Student.objects.exclude(face_image="").count()
    missing_files = 0
    encodings_available = Student.objects.exclude(face_encoding=None).count()
    faces_detected = 0
    try:
        import cv2
        import face_recognition
    except Exception:
        libs_status = "missing"
        return render(request, "attendance/self_check.html", {
            "libs_status": libs_status,
            "camera_status": camera_status,
            "total_students": total_students,
            "with_images": with_images,
            "missing_files": missing_files,
            "encodings_available": encodings_available,
            "faces_detected": faces_detected
        })
    students = Student.objects.all()
    for s in students:
        if s.face_image and not os.path.exists(s.face_image.path):
            missing_files += 1
    cam = None
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            cam = cv2.VideoCapture(1)
        if cam and cam.isOpened():
            camera_status = "ok"
            ret, frame = cam.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                faces = face_recognition.face_locations(rgb)
                faces_detected = len(faces)
    finally:
        if cam:
            cam.release()
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
    return render(request, "attendance/self_check.html", {
        "libs_status": libs_status,
        "camera_status": camera_status,
        "total_students": total_students,
        "with_images": with_images,
        "missing_files": missing_files,
        "encodings_available": encodings_available,
        "faces_detected": faces_detected
    })
 

def faculty_mark_present(request, id):
    rec = Attendance.objects.get(id=id)
    rec.status = True
    rec.last_marked_at = timezone.now()
    rec.save()
    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("attendance_dashboard")


def faculty_mark_absent(request, id):
    rec = Attendance.objects.get(id=id)
    rec.status = False
    rec.last_marked_at = timezone.now()
    rec.save()
    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("attendance_dashboard")


def upload_mark(request):
    if request.method == "POST":
        try:
            import face_recognition
        except Exception:
            messages.error(request, "Face recognition libs missing")
            return redirect("dashboard")
        file = request.FILES.get("image")
        if not file:
            messages.error(request, "No image uploaded")
            return redirect("dashboard")
        import tempfile
        import os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp.flush()
        tmp.close()
        try:
            img = face_recognition.load_image_file(tmp.name)
            encs = face_recognition.face_encodings(img)
            if not encs:
                messages.error(request, "No face detected in uploaded image")
                return redirect("dashboard")
            enc = encs[0]
            students = Student.objects.all()
            known = []
            known_students = []
            for s in students:
                if s.face_encoding:
                    known.append(s.face_encoding)
                    known_students.append(s)
            if not known:
                messages.error(request, "No stored encodings found")
                return redirect("dashboard")
            distances = face_recognition.face_distance(known, enc)
            try:
                distances_list = distances.tolist()
            except Exception:
                distances_list = list(distances)
            idx = min(range(len(distances_list)), key=lambda i: distances_list[i])
            best = distances_list[idx]
            if best <= getattr(settings, "FACE_MATCH_THRESHOLD", 0.6):
                student = known_students[idx]
                Attendance.objects.update_or_create(
                    student=student,
                    date=date.today(),
                    defaults={"status": True, "last_marked_at": timezone.now()}
                )
                messages.success(request, f"Marked {student.name} present")
            else:
                messages.error(request, "No match found for uploaded image")
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass
        return redirect("dashboard")
    return render(request, "attendance/upload.html")


# ✅ Absentee Detection + Notification Simulation
def absentee_list(request):
    today = date.today()
    absentees = Attendance.objects.filter(date=today, status=False).select_related("student").order_by("student__name")
    notifications = [f"Notification sent to Parent of {a.student.name} ({a.student.parent_email})" for a in absentees]
    return render(request, "attendance/absentees.html", {"absentees": absentees, "notifications": notifications})


def admin_tools(request):
    today = date.today()
    records = Attendance.objects.filter(date=today)
    present_count = records.filter(status=True).count()
    absent_count = records.filter(status=False).count()
    total_count = records.count()
    attendance_percentage = round((present_count / total_count) * 100) if total_count else 0
    return render(request, "attendance/admin_tools.html", {
        "present_count": present_count,
        "absent_count": absent_count,
        "total_count": total_count,
        "attendance_percentage": attendance_percentage,
    })


def reset_today_statuses(request):
    Attendance.objects.filter(date=date.today()).update(status=False, last_marked_at=None)
    return redirect("admin_tools")
