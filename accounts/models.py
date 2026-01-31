from django.db import models

# Student Model
class Student(models.Model):
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    parent_email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.reg_no})"


# Faculty Model
class Faculty(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} - {self.department}"

# Create your models here.
