from django.contrib import admin
from .models import Student, Faculty


class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "reg_no", "email", "parent_email")
    search_fields = ("name", "reg_no", "email", "parent_email")


class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "email")
    search_fields = ("name", "department", "email")


admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.site_header = "Campus Admin"
admin.site.site_title = "Campus Admin"
admin.site.index_title = "Administration"
