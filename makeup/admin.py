from django.contrib import admin
from .models import MakeupClass, RemedialAttendance


class MakeupClassAdmin(admin.ModelAdmin):
    list_display = ("subject", "faculty", "date", "remedial_code")
    list_filter = ("faculty", "date")
    search_fields = ("subject", "remedial_code", "faculty__name")


class RemedialAttendanceAdmin(admin.ModelAdmin):
    list_display = ("makeup_class", "student", "marked")
    list_filter = ("marked",)
    search_fields = ("makeup_class__subject", "student__name", "student__reg_no")


admin.site.register(MakeupClass, MakeupClassAdmin)
admin.site.register(RemedialAttendance, RemedialAttendanceAdmin)
