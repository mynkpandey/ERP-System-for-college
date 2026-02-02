from django.db import models

# Student Model
class Student(models.Model):
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    parent_email = models.EmailField()
    face_image = models.ImageField(upload_to="faces/", blank=True, null=True)
    face_encoding = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.reg_no})"

    def save(self, *args, **kwargs):
        if self.face_image and not self.face_encoding:
            try:
                import face_recognition
                import os
                if os.path.exists(self.face_image.path):
                    img = face_recognition.load_image_file(self.face_image.path)
                    encodings = face_recognition.face_encodings(img)
                    if len(encodings) > 0:
                        try:
                            self.face_encoding = encodings[0].tolist()
                        except Exception:
                            self.face_encoding = list(encodings[0])
            except Exception:
                pass
        super().save(*args, **kwargs)


# Faculty Model
class Faculty(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} - {self.department}"

# Create your models here.
