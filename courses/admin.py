from django.contrib import admin
from .models import Course, ClassGroup, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher')
    search_fields = ('title',)


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_active')
    list_filter = ('course', 'is_active')
    search_fields = ('title',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_group', 'enrolled_at')
    list_filter = ('class_group__course',)
