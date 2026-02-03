import os
from datetime import date

from accounts.models import Student
from attendance.models import Attendance
from django.utils import timezone
from django.conf import settings


def mark_attendance_camera():
    try:
        import cv2
        import face_recognition
    except Exception:
        return False, "Required camera libraries are missing"
    students = Student.objects.all()
    if not students.exists():
        return False, "No students registered"
    known_encodings = []
    known_students = []
    for student in students:
        if student.face_encoding:
            known_encodings.append(student.face_encoding)
            known_students.append(student)
            continue
        if not student.face_image:
            continue
        if not os.path.exists(student.face_image.path):
            continue
        img = face_recognition.load_image_file(student.face_image.path)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            try:
                student.face_encoding = encodings[0].tolist()
            except Exception:
                student.face_encoding = list(encodings[0])
            student.save(update_fields=["face_encoding"])
            known_encodings.append(student.face_encoding)
            known_students.append(student)
    if len(known_encodings) == 0:
        return False, "No valid student face encodings"
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        cam = cv2.VideoCapture(1)
        if not cam.isOpened():
            return False, "Camera is not available"
    stable_index = None
    stable_count = 0
    required_stable = getattr(settings, "FACE_STABLE_FRAMES", 3)
    threshold = getattr(settings, "FACE_MATCH_THRESHOLD", 0.6)
    margin_req = getattr(settings, "FACE_MARGIN", 0.08)
    while True:
        ret, frame = cam.read()
        if not ret:
            cam.release()
            cv2.destroyAllWindows()
            return False, "Failed to read from camera"
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(frame_rgb)
        face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
        for face_encoding in face_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            try:
                distances_list = distances.tolist()
            except Exception:
                distances_list = list(distances)
            if not distances_list:
                continue
            best_index = min(range(len(distances_list)), key=lambda i: distances_list[i])
            best_distance = distances_list[best_index]
            second_distance = None
            if len(distances_list) > 1:
                second_distance = sorted(distances_list)[1]
            margin_ok = True
            if second_distance is not None:
                margin_ok = (second_distance - best_distance) >= margin_req
            if best_distance <= threshold and margin_ok:
                if stable_index == best_index:
                    stable_count += 1
                else:
                    stable_index = best_index
                    stable_count = 1
                if stable_count >= required_stable:
                    student = known_students[best_index]
                    Attendance.objects.update_or_create(
                        student=student,
                        date=date.today(),
                        defaults={"status": True, "last_marked_at": timezone.now()}
                    )
                    cam.release()
                    cv2.destroyAllWindows()
                    return True, f"Marked {student.name} present"
            else:
                stable_index = None
                stable_count = 0
        cv2.imshow("Attendance Camera - Press Q", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cam.release()
            cv2.destroyAllWindows()
            return False, "Camera closed without marking"
