# Smart AI-Enabled LPU Campus Management System

## Overview
This project implements the required modules for LPU’s Smart Campus Management System using Django. It includes Smart Attendance with optional AI face recognition, Food Stall pre-ordering with peak analysis, Campus Resource estimation, and Make-Up class with remedial code. Admin panel and exports are provided.

## Tech Stack
- Backend: Django 5.2.x
- DB: SQLite (dev)
- Optional AI: face_recognition + OpenCV for camera attendance
- Env: python-decouple for .env

## Run Instructions
- Set .env (SECRET_KEY, DEBUG, ALLOWED_HOSTS, ADMIN_* credentials)
- Initialize and run:
  - `python manage.py migrate`
  - `python manage.py bootstrap_admin`
  - `python manage.py runserver`
- Admin: http://localhost:8000/admin/

## Module Mapping
- Smart Attendance
  - Faculty one-click sheet: [attendance/views.py](attendance/views.py)
  - Camera attendance: [attendance/utils.py](attendance/utils.py), [attendance/views.py](attendance/views.py)
  - Absentees + notifications (simulated): [attendance/views.py](attendance/views.py), [attendance/templates/attendance/absentees.html](attendance/templates/attendance/absentees.html)
  - Finalize & export Excel (.xlsx): current hour and per-slot: [attendance/views.py](attendance/views.py), [attendance/templates/attendance/dashboard.html](attendance/templates/attendance/dashboard.html)
- Smart Food Stall
  - Pre-order and time slot selection: [food/views.py](food/views.py), [food/templates](food/templates)
  - Peak times view: [food/views.py](food/views.py), [food/templates/food/peak.html](food/templates/food/peak.html)
- Campus Resource & Parameters
  - Models: Blocks, Classrooms, Courses, Faculty, Students: [resources/models.py](resources/models.py), [accounts/models.py](accounts/models.py)
  - Admin dashboards: [resources/admin.py](resources/admin.py), [accounts/admin.py](accounts/admin.py)
- Make-Up Class & Remedial
  - Remedial code generation and attendance: [makeup/views.py](makeup/views.py), [makeup/templates](makeup/templates)

## AI Integration (Optional)
- Face recognition attendance
  - Configurable thresholds in settings: FACE_MATCH_THRESHOLD, FACE_MARGIN, FACE_STABLE_FRAMES
  - Self-check diagnostics: /attendance/self-check/
  - Stored student face encodings to improve speed and reliability
- Rush prediction (optional extension)
  - Can be added in food module using historical slot demand

## Exports
- Finalize Selected Slot & Export Excel: generates .xlsx with Registration Number, Name, Marked At, Faculty
- Files download via browser and can also be generated via admin actions or a management command

## Admin Panel
- Custom site branding
- Manage Students, Faculty, Attendance, Resources, Food, and Makeup modules
- Attendance actions: export current hour to exports/, reset today’s statuses
- Bootstrap command creates superuser from env variables

## Evaluation Scheme (Suggested)
- Correctness & Completeness (40%)
  - All mandatory modules functional and integrated
  - Attendance updates instantly; absentees detected; notifications simulated
  - Food ordering with time slots; peak time analysis
  - Resources stored; basic capacity/utilization displayed
  - Make-up classes with remedial code; separate attendance maintained
- AI Integration (20%)
  - Face recognition attendance works reliably (thresholds, stability, diagnostics)
  - Optional prediction or scheduling features (bonus)
- UX & Usability (15%)
  - Clear dashboards, flows, error handling, messages
  - Admin usability for data management
- Code Quality & Security (15%)
  - Clean structure, settings via env, no secrets in code
  - Unique constraints, data validation
- Documentation & Deployment (10%)
  - README, setup, admin instructions, exports
  - Demo steps and sample data guidance

## Demo Script Checklist
- Add Students with face images in Admin
- Open Attendance dashboard; auto-create today’s records
- Mark via camera and see Present update + message
- View absentees; see simulated notifications
- Export per-slot Excel and verify Name/Reg no/time/faculty
- Place food orders and view peak times
- Create resources and courses; inspect admin reports
- Create make-up class; generate code; mark attendance via code

## Notes
- Face libraries require installation of dlib/OpenCV; use self-check to verify availability
- For demo without camera, consider image upload attendance or mock mode

