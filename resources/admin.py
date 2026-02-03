from django.contrib import admin
from .models import Block, Classroom, Course


class BlockAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("block", "room_number", "capacity")
    list_filter = ("block",)
    search_fields = ("room_number",)


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty")
    list_filter = ("faculty",)
    search_fields = ("name", "faculty__name")


admin.site.register(Block, BlockAdmin)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Course, CourseAdmin)
