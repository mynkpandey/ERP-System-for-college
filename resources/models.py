from django.db import models
from accounts.models import Faculty, Student


# ✅ Block Model
class Block(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ✅ Classroom Model
class Classroom(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.block.name} - {self.room_number}"


# ✅ Course Model
class Course(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.name
