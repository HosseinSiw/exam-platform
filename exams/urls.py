from django.urls import path

from .views import (
    StudentClassExamListView,ExamStartView,
    ExamTakeView, FinishExamView, ExamSummaryView
)


app_name = 'exams'

urlpatterns = [
    path(
        'class/<int:class_group_id>/',
        StudentClassExamListView.as_view(),
        name='class-exam-list'
    ),
    path(
        'class/<int:class_group_id>/exam/<int:exam_id>/start/',
        ExamStartView.as_view(),
        name='start'
    ),
    path(
        'class/<int:class_group_id>/exam/<int:exam_id>/take/',
        ExamTakeView.as_view(),
        name='take',
    ),
    path(
        'exam/class/<int:class_group_id>/exam/<int:exam_id>/finish/',
        FinishExamView.as_view(),
        name='finish',
    ),
    path(
        "class/<int:class_group_id>/exam/<int:exam_id>/summary/",
        ExamSummaryView.as_view(),
        name="summary"
    )
]
