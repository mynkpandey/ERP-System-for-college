from django.db import models
from datetime import date
from accounts.models import Student, Faculty


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    date = models.DateField(default=date.today)  # ✅ Correct

    status = models.BooleanField(default=False)
    last_marked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.date}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "date"], name="unique_attendance_per_student_day")
        ]
