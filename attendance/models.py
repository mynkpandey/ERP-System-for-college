# Create your models here.
from django.db import models
from accounts.models import Student, Faculty


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    date = models.DateField(auto_now_add=True)

    status = models.BooleanField(default=False)
    # False = Absent
    # True = Present

    def __str__(self):
        return f"{self.student.name} - {self.date} - {'Present' if self.status else 'Absent'}"
