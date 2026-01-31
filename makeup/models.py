from django.db import models
from accounts.models import Faculty, Student


# ✅ Faculty schedules makeup class + code generated
class MakeupClass(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateField()

    remedial_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.subject} ({self.remedial_code})"


# ✅ Separate attendance record for remedial class
class RemedialAttendance(models.Model):
    makeup_class = models.ForeignKey(MakeupClass, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    marked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.makeup_class.subject}"
