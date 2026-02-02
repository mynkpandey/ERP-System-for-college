import cv2
import face_recognition
import os
from datetime import date

from accounts.models import Student
from attendance.models import Attendance


def mark_attendance_camera():
    """
    Opens camera → detects face → matches student → marks attendance present
    """

    # ✅ Load all registered students
    students = Student.objects.all()

    if not students.exists():
        print("❌ No students registered!")
        return

    known_encodings = []
    known_students = []

    print("📌 Loading student face data...")

    # =====================================================
    # ✅ Step 1: Load all student face encodings
    # =====================================================
    for student in students:

        # Skip if no image uploaded
        if not student.face_image:
            print(f"⚠ No face image for {student.name}")
            continue

        # Skip if file missing
        if not os.path.exists(student.face_image.path):
            print(f"❌ File missing for {student.name}")
            continue

        # Load image
        img = face_recognition.load_image_file(student.face_image.path)

        # Get encoding
        encodings = face_recognition.face_encodings(img)

        if len(encodings) == 0:
            print(f"⚠ No face detected in image of {student.name}")
            continue

        known_encodings.append(encodings[0])
        known_students.append(student)

    if len(known_encodings) == 0:
        print("❌ No valid student faces found!")
        return

    print("✅ Face data loaded successfully!")

    # =====================================================
    # ✅ Step 2: Start Camera
    # =====================================================
    cam = cv2.VideoCapture(0)

    print("\n🎥 Camera Started...")
    print("Press Q to exit\n")

    while True:
        ret, frame = cam.read()

        if not ret:
            print("❌ Camera not working!")
            break

        # Convert BGR → RGB (important)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in live camera
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # =====================================================
        # ✅ Step 3: Match Face
        # =====================================================
        for face_encoding, face_location in zip(face_encodings, face_locations):

            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=0.5
            )

            if True in matches:
                index = matches.index(True)

                # ✅ Student matched
                student = known_students[index]

                # ✅ Mark attendance only once per day
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=date.today(),
                    defaults={"status": True}
                )

                # Draw rectangle + name
                top, right, bottom, left = face_location

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{student.name} Present",
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                print("✅ Attendance Marked:", student.name)

                # Show frame for 2 seconds then close
                cv2.imshow("Attendance Camera", frame)
                cv2.waitKey(2000)

                cam.release()
                cv2.destroyAllWindows()
                return

        # =====================================================
        # Show Camera Window
        # =====================================================
        cv2.imshow("Attendance Camera - Press Q", frame)

        # Exit if Q pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("❌ Attendance cancelled by user")
            break

    cam.release()
    cv2.destroyAllWindows()
