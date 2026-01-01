from django.urls import path
from .views import (
    StudentResultListView,
    StudentResultDetailView,
)

app_name = "results"

urlpatterns = [
    path("my/", StudentResultListView.as_view(), name="student_results_list"),
    path("my/<int:pk>/", StudentResultDetailView.as_view(), name="student_result_detail"),
]
