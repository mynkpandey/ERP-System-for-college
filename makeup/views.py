from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
import random
from .models import MakeupClass, RemedialAttendance
from accounts.models import Student, Faculty


# ✅ Student enters remedial code and marks attendance
def enter_remedial_code(request):

    students = Student.objects.all()

    if request.method == "POST":

        code = (request.POST.get("code") or "").strip()
        student_id = (request.POST.get("student") or "").strip()

        # ✅ Safety Check
        if not code or not student_id:
            return render(request, "makeup/enter_code.html", {
                "students": students,
                "error": "⚠ Please enter code and select student!"
            })

        # ✅ Find Makeup Class by Code
        try:
            makeup_class = MakeupClass.objects.get(remedial_code=code)
        except MakeupClass.DoesNotExist:
            return render(request, "makeup/enter_code.html", {
                "students": students,
                "error": "❌ Invalid Remedial Code!"
            })

        # ✅ Get Student
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return render(request, "makeup/enter_code.html", {
                "students": students,
                "error": "❌ Invalid Student selection!"
            })

        # ✅ Mark Remedial Attendance
        record, created = RemedialAttendance.objects.get_or_create(
            makeup_class=makeup_class,
            student=student
        )

        record.marked = True
        record.save()

        # ✅ Success Page
        return render(request, "makeup/success.html", {
            "student": student,
            "makeup_class": makeup_class
        })

    # ✅ GET Request Page Load
    return render(request, "makeup/enter_code.html", {
        "students": students
    })


# ==========================================================
# ✅ Faculty Dashboard: Present Students + Absentees Detection
# ==========================================================

def makeup_dashboard(request):

    classes = MakeupClass.objects.all()
    students = Student.objects.all()

    dashboard_data = []
    total_present = 0
    total_absent = 0

    for cls in classes:

        # ✅ Present Students (marked=True)
        present_records = RemedialAttendance.objects.filter(
            makeup_class=cls,
            marked=True
        )

        present_students = [r.student for r in present_records]

        # ❌ Absentees = All Students - Present Students
        absent_students = students.exclude(
            id__in=[s.id for s in present_students]
        )

        dashboard_data.append({
            "class": cls,
            "present": present_students,
            "absent": absent_students
        })
        total_present += len(present_students)
        total_absent += len(list(absent_students))

    return render(request, "makeup/dashboard.html", {
        "dashboard_data": dashboard_data,
        "total_classes": len(dashboard_data),
        "total_present": total_present,
        "total_absent": total_absent
    })


def add_makeup_class(request):
    faculties = Faculty.objects.all()
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        faculty_id = request.POST.get("faculty")
        date_str = request.POST.get("date")
        code_input = request.POST.get("remedial_code", "").strip()
        if not subject or not faculty_id or not date_str:
            return render(request, "makeup/add_class.html", {
                "faculties": faculties,
                "error": "Please fill all required fields"
            })
        try:
            faculty = Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            return render(request, "makeup/add_class.html", {
                "faculties": faculties,
                "error": "Invalid faculty"
            })
        try:
            date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return render(request, "makeup/add_class.html", {
                "faculties": faculties,
                "error": "Invalid date format"
            })
        code = code_input
        if not code:
            while True:
                code = f"{random.randint(100000, 999999)}"
                if not MakeupClass.objects.filter(remedial_code=code).exists():
                    break
        else:
            if MakeupClass.objects.filter(remedial_code=code).exists():
                return render(request, "makeup/add_class.html", {
                    "faculties": faculties,
                    "error": "Remedial code already exists"
                })
        cls = MakeupClass.objects.create(
            faculty=faculty,
            subject=subject,
            date=date_val,
            remedial_code=code
        )
        messages.success(request, "Makeup class created")
        return redirect("makeup_dashboard")
    generated_code = f"{random.randint(100000, 999999)}"
    return render(request, "makeup/add_class.html", {
        "faculties": faculties,
        "generated_code": generated_code
    })
