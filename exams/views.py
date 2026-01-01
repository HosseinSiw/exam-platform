from django.views import View
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseNotAllowed
from django.db import transaction, IntegrityError
from django.db.models import Count, Q
from django.contrib import messages

from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now

from datetime import timedelta

from .models import Exam, StudentExam, Question, Answer
from .mixins import ExamAccessMixin
from courses.models import Enrollment, ClassGroup
from exams.services.grading import ExamGradingService
from exams.tasks import grade_exam_task

import logging

logger = logging.getLogger('apps.exams')

class StudentClassExamListView(LoginRequiredMixin, ListView):
    template_name = "exams/student_exam_list.html"
    context_object_name = "exams"
    paginate_by = 20  # pagination

    def dispatch(self, request, *args, **kwargs):
        self.class_group = get_object_or_404(
            ClassGroup.objects.select_related("course"),
            id=kwargs["class_group_id"],
            is_active=True,
        )

        if not Enrollment.objects.filter(
            student=request.user,
            class_group=self.class_group,
            is_active=True,
        ).exists():
            raise PermissionDenied("شما در این کلاس شرکت نکرده اید")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Exam.objects.filter(
                class_groups=self.class_group,
                is_active=True,
            )
            .select_related("course")
            .prefetch_related("class_groups")
            .distinct()
            .order_by("start_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "class_group": self.class_group,
            "course": self.class_group.course,
        })
        return context

class ExamStartView(ExamAccessMixin, View):
    """
    Production responsibilities:
    - atomic StudentExam creation
    - hard retake prevention
    - idempotent POST
    - race-condition safe
    """

    template_name = "exams/exam_start.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            "exam": self.exam
        })

    def post(self, request, *args, **kwargs):
        exam = self.exam
        student = request.user
        now = timezone.now()

        try:
            with transaction.atomic():
                student_exam, created = (
                    StudentExam.objects
                    .select_for_update()
                    .get_or_create(
                        student=student,
                        exam=exam,
                        defaults={"started_at": now}
                    )
                )

                # hard retake guard
                if not created and student_exam.finished_at:
                    raise PermissionDenied("شما قبلاً در این آزمون شرکت کرده‌اید")

                # idempotent start
                if not student_exam.started_at:
                    student_exam.started_at = now
                    student_exam.save(update_fields=["started_at"])

        except IntegrityError:
            messages.error(request, "خطا در شروع آزمون، دوباره تلاش کنید")
            return redirect(request.path)

        return redirect(
            "exams:take",
            class_group_id=kwargs["class_group_id"],
            exam_id=exam.id
        )
        
        
class ExamTakeView(ExamAccessMixin, View):
    template_name = "exams/exam_take.html"
    auto_submit_template_name = "exams/exam_autosubmit.html"
    allow_existing_attempt = True

    # ---------- Core helpers ----------

    def get_student_exam(self):
        try:
            student_exam = (
                StudentExam.objects
                .select_related("exam")
                .get(student=self.request.user, exam=self.exam)
            )
        except StudentExam.DoesNotExist:
            raise Http404("Exam not started.")

        if not student_exam.started_at:
            raise Http404("Exam not started.")

        return student_exam

    def is_time_over(self, student_exam):
        if not self.exam.duration_minutes:
            return False

        end_time = student_exam.started_at + timedelta(
            minutes=self.exam.duration_minutes
        )
        return timezone.now() >= end_time

    def get_questions(self):
        return (
            Question.objects
            .filter(exam=self.exam)
            .prefetch_related("options")
        )

    # ---------- HTTP methods ----------

    def get(self, request, *args, **kwargs):
        student_exam = self.get_student_exam()

        # already finished → summary (safe, idempotent)
        if student_exam.finished_at:
            return redirect(
                "exams:summary",
                class_group_id=self.class_group.id,
                exam_id=self.exam.id,
            )

        # timeout (GET → NO redirect to finish)
        if self.is_time_over(student_exam):
            messages.warning(
                request,
                "زمان آزمون به پایان رسید. پاسخ‌ها در حال ثبت نهایی هستند."
            )
            return render(
                request,
                self.auto_submit_template_name,
                {
                    "exam": self.exam,
                    "student_exam": student_exam,
                    "class_group": self.class_group,
                }
            )

        answers_dict = {
            a.question_id: a.selected_option_id
            for a in self.student_exam.answers.all()
        }
        # normal exam page
        return render(
            request,
            self.template_name,
            {
                "exam": self.exam,
                "student_exam": student_exam,
                "questions": self.get_questions(),
                "class_group": self.class_group,
                "answers_dict": answers_dict,
            }
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        student_exam = (
            StudentExam.objects
            .select_for_update()
            .get(student=request.user, exam=self.exam)
        )

        #  finished → summary (hard lock)
        if student_exam.finished_at:
            return redirect(
                "exams:summary",
                class_group_id=self.class_group.id,
                exam_id=self.exam.id,
            )

        # timeout during POST → finish (valid place for redirect)
        if self.is_time_over(student_exam):
            messages.warning(request, "زمان آزمون به پایان رسید")
            return redirect(
                "exams:finish",
                class_group_id=self.class_group.id,
                exam_id=self.exam.id,
            )

        questions = self.get_questions()

        for question in questions:
            option_id = request.POST.get(f"question_{question.id}")

            selected_option = None
            if option_id:
                selected_option = question.options.filter(
                    id=option_id
                ).first()

            Answer.objects.update_or_create(
                student_exam=student_exam,
                question=question,
                defaults={
                    "selected_option": selected_option,
                    "is_correct": False,  # grading handled later
                }
                        )
            
            
        # PRG pattern (POST → Redirect → GET)
        return redirect(
            "exams:take",
            class_group_id=self.class_group.id,
            exam_id=self.exam.id,
        )


class FinishExamView(ExamAccessMixin, View):
    """
    Finalizes a student exam attempt and locks further changes.
    POST-only, idempotent, production-safe.
    """
    allow_existing_attempt = True

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])

    def post(self, request, *args, **kwargs):
        logger.info(
            "exam_finish_requested",
            extra={
                "student_exam_id": student_exam.id,
                "student_id": request.user.id,
                "exam_id": student_exam.exam_id,
            },
        )

        with transaction.atomic():
            try:
                student_exam = (
                    StudentExam.objects
                    .select_for_update()
                    .select_related("exam")
                    .get(student=request.user, exam=self.exam)
                )
            except StudentExam.DoesNotExist:
                raise Http404("StudentExam not found.")

            # must be started
            if not student_exam.started_at:
                raise Http404("Exam has not been started yet.")

            # idempotent finish
            if student_exam.is_finished:
                logger.warning(
                    "exam_finish_duplicate_request",
                    extra={"student_exam_id": student_exam.id, 
                       "user": student_exam.student.mobile},
                )
                return redirect(
                    "exams:summary",
                    class_group_id=self.class_group.id,
                    exam_id=self.exam.id,
                )

            # hard guard: no empty submission
            if not student_exam.answers.exists():
                messages.error(request, "هیچ پاسخی ثبت نشده است")
                return redirect(
                    "exams:take",
                    class_group_id=self.class_group.id,
                    exam_id=self.exam.id,
                )

            # state change only
            student_exam.finish()
            transaction.on_commit(
                lambda: grade_exam_task.delay(student_exam.id)
            )
        

        return redirect(
            "exams:summary",
            class_group_id=self.class_group.id,
            exam_id=self.exam.id,
        )
        
        
class ExamSummaryView(ExamAccessMixin, TemplateView):
    template_name = "exams/exam_summary.html"
    allow_existing_attempt = True

    # ---------- Core ----------

    def get_student_exam(self):
        try:
            return (
                StudentExam.objects
                .select_related("exam")
                .get(student=self.request.user, exam=self.exam)
            )
        except StudentExam.DoesNotExist:
            raise Http404("StudentExam not found.")

    def dispatch(self, request, *args, **kwargs):
        #  FIRST: let ExamAccessMixin prepare exam & class_group
        response = super().dispatch(request, *args, **kwargs)

        # now self.exam & self.class_group exist
        self.student_exam = self.get_student_exam()

        # must be finished
        if not self.student_exam.is_finished:
            return redirect(
                "exams:take",
                class_group_id=self.class_group.id,
                exam_id=self.exam.id,
            )

        return response

    # ---------- Context ----------

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        answers = (
            Answer.objects
            .filter(student_exam=self.student_exam)
            .select_related("question", "selected_option")
            .order_by("question__order")
        )

        stats = answers.aggregate(
            correct=Count("id", filter=Q(is_correct=True)),
            wrong=Count(
                "id",
                filter=Q(is_correct=False, selected_option__isnull=False),
            ),
            blank=Count("id", filter=Q(selected_option__isnull=True)),
        )

        context.update({
            "student_exam": self.student_exam,
            "exam": self.exam,
            "answers": answers,

            # DB-driven statistics
            "correct_count": stats["correct"],
            "wrong_count": stats["wrong"],
            "blank_count": stats["blank"],

            #  source of truth = questions
            "total_questions": self.exam.questions.count(),

            # derived state
            "pure_percentage": self.student_exam.percentage(),
        })

        return context
    