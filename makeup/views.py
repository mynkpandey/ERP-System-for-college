from django.shortcuts import render
from .models import MakeupClass, RemedialAttendance
from accounts.models import Student


# ✅ Student enters remedial code and marks attendance
def enter_remedial_code(request):

    students = Student.objects.all()

    if request.method == "POST":

        code = request.POST.get("code")
        student_id = request.POST.get("student")

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
        student = Student.objects.get(id=student_id)

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

    return render(request, "makeup/dashboard.html", {
        "dashboard_data": dashboard_data
    })
