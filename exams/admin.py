from django.contrib import admin
from .models import (
    Exam, Question, QuestionOption,
    StudentExam, Answer
)
from django.core.exceptions import ValidationError
from .forms import ExamAdminForm


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'exam',
        'text',
        # 'question_type',
        'order',
    )
    list_filter = ('exam',)
    search_fields = ('text',)
    inlines = (QuestionOptionInline,)
    ordering = ('exam', 'order')



@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    form = ExamAdminForm

    list_display = (
        'title',
        'course',
        "grading_policy",
        'start_at',
        'end_at',
        'is_active',
    )

    list_filter = (
        'course',
        'is_active',
        'start_at',
    )

    search_fields = (
        'title',
        'course__title',
    )

    filter_horizontal = ('class_groups',)

    ordering = ('-start_at',)


@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'student', 'exam',
        'started_at', 'finished_at',
        'score'
    )
    readonly_fields = (
        'student', 'exam',
        'started_at', 'finished_at',
        'score'
    )

    def has_add_permission(self, request):
        return False



@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_exam', 'question', 'is_correct')
    readonly_fields = ('student_exam', 'question', 'selected_option', 'is_correct')

    def has_add_permission(self, request):
        return False

