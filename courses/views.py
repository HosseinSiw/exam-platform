from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from .models import Course
from .mixins import StudentEnrolledRequiredMixin


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/student_course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        qs =  Course.objects.filter(
        enrollments__student=self.request.user
        ).distinct()
        return qs
    
class StudentCourseDetailView(
    LoginRequiredMixin,
    DetailView, StudentEnrolledRequiredMixin
):
    model = Course
    pk_url_kwarg = 'course_id'
    template_name = 'courses/student_course_details.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['class_groups'] = (
            self.object.class_groups.filter(
                enrollments__student=self.request.user
            )
        )
        return context
