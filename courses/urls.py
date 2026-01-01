from django.urls import path
from .views import StudentCourseListView, StudentCourseDetailView
app_name = 'courses'

urlpatterns = [
    path('', StudentCourseListView.as_view(), name='student_list'),
    path('<int:course_id>/', StudentCourseDetailView.as_view(), name='detail'),
]
