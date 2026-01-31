from django.shortcuts import render
from .models import Block, Classroom, Course
from accounts.models import Faculty, Student


# ✅ Resource Utilization Dashboard
def resource_dashboard(request):

    # Total Blocks
    total_blocks = Block.objects.count()

    # Total Classrooms
    total_rooms = Classroom.objects.count()

    # Total Capacity
    total_capacity = sum(room.capacity for room in Classroom.objects.all())

    # Total Students
    total_students = Student.objects.count()

    # Capacity Utilization %
    utilization = 0
    if total_capacity > 0:
        utilization = (total_students / total_capacity) * 100

    # Faculty Workload Distribution
    faculty_workload = []
    faculties = Faculty.objects.all()

    for faculty in faculties:
        courses_count = Course.objects.filter(faculty=faculty).count()
        faculty_workload.append({
            "name": faculty.name,
            "courses": courses_count
        })

    return render(request, "resources/dashboard.html", {
        "total_blocks": total_blocks,
        "total_rooms": total_rooms,
        "total_capacity": total_capacity,
        "total_students": total_students,
        "utilization": round(utilization, 2),
        "faculty_workload": faculty_workload
    })
