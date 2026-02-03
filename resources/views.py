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

    # Additional statistics for enhanced template
    course_counts = [f['courses'] for f in faculty_workload]
    max_courses = max(course_counts, default=0)
    avg_courses = sum(course_counts) / len(course_counts) if course_counts else 0
    high_workload_count = sum(1 for c in course_counts if c >= 4)
    medium_workload_count = sum(1 for c in course_counts if 2 <= c < 4)
    low_workload_count = sum(1 for c in course_counts if c < 2)

    return render(request, "resources/dashboard.html", {
        "total_blocks": total_blocks,
        "total_rooms": total_rooms,
        "total_capacity": total_capacity,
        "total_students": total_students,
        "utilization": round(utilization, 2),
        "faculty_workload": faculty_workload,
        "max_courses": max_courses,
        "avg_courses": round(avg_courses, 1),
        "high_workload_count": high_workload_count,
        "medium_workload_count": medium_workload_count,
        "low_workload_count": low_workload_count
    })
