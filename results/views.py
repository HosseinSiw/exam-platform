from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from exams.models import StudentExam


class StudentResultListView(LoginRequiredMixin, ListView):
    template_name = "results/student_result_list.html"
    context_object_name = "student_exams"
    paginate_by = 10

    def get_queryset(self):
        return (
            StudentExam.objects
            .select_related("exam")
            .filter(
                student=self.request.user,
                finished_at__isnull=False,
                graded_at__isnull=False,
            )
            .order_by("-finished_at")
        )

class StudentResultDetailView(LoginRequiredMixin, DetailView):
    template_name = "results/student_result_detail.html"
    context_object_name = "student_exam"

    def get_queryset(self):
        return (
            StudentExam.objects
            .filter(
                student=self.request.user,
                finished_at__isnull=False,
                graded_at__isnull=False,
            )
            .select_related("exam")
            .prefetch_related(
                "answers",
                "answers__question",
                "answers__selected_option",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        se = self.object

        # Aggregate answer stats
        stats = se.answers.aggregate(
            correct_count=Count("id", filter=Q(is_correct=True)),
            wrong_count=Count(
                "id",
                filter=Q(is_correct=False, selected_option__isnull=False),
            ),
            blank_count=Count("id", filter=Q(selected_option__isnull=True)),
        )

        total_questions = se.exam.questions.count()

        # Defensive: avoid division by zero or corrupted data
        percentage = (
            round((stats["correct_count"] / total_questions) * 100, 2)
            if total_questions > 0
            else 0
        )

        context.update({
            "stats": stats,
            "total_questions": total_questions,
            "percentage": percentage,
            "score": se.score,  # single source for template
        })
        return context