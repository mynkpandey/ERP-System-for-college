from django.db import migrations, models


def dedupe(apps, schema_editor):
    Attendance = apps.get_model("attendance", "Attendance")
    seen = {}
    for rec in Attendance.objects.all().order_by("id"):
        key = (rec.student_id, rec.date)
        seen.setdefault(key, []).append(rec)
    for key, lst in seen.items():
        if len(lst) > 1:
            keeper = None
            for r in lst:
                if r.status:
                    keeper = r
                    break
            if keeper is None:
                keeper = lst[0]
            for r in lst:
                if r.id != keeper.id:
                    r.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_attendance_last_marked_at"),
    ]

    operations = [
        migrations.RunPython(dedupe, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="attendance",
            constraint=models.UniqueConstraint(
                fields=["student", "date"],
                name="unique_attendance_per_student_day",
            ),
        ),
    ]
