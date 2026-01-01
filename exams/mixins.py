from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages

from courses.models import ClassGroup, Enrollment
from exams.models import Exam, StudentExam
import logging

logger = logging.getLogger('apps.exams')

class ExamAccessMixin:
    """
    UX-first Exam Access Controller

    - Never raises business PermissionDenied
    - Redirects user to the closest valid state
    - Guarantees exam + class_group integrity
    """

    exam_url_kwarg = "exam_id"
    class_group_url_kwarg = "class_group_id"
    allow_existing_attempt = False

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # role check
        if user.role != "student":
            messages.error(request, "دسترسی به آزمون فقط برای دانش‌آموزان ممکن است.")
            logger.warning(
            "exam_permission_denied",
            extra={
                "user_id": self.request.user.id,
            },
            )
            return redirect("home:home")

        # class group
        try:
            self.class_group = ClassGroup.objects.get(
                id=kwargs[self.class_group_url_kwarg],
                is_active=True,
            )
        except ClassGroup.DoesNotExist:
            messages.error(request, "کلاس مورد نظر یافت نشد یا غیرفعال است.")
            return redirect("courses:my-classes")

        # enrollment
        if not Enrollment.objects.filter(
            student=user,
            class_group=self.class_group,
        ).exists():
            messages.error(request, "شما عضو این کلاس نیستید.")
            logger.warning(
            "class_permission_denied",
            extra={
                "user_id": self.request.user.id,
                "class_id": self.class_group.id,
            },
            )
            return redirect(
                reverse(
                    "courses:class-detail",
                    kwargs={"class_group_id": self.class_group.id},
                )
            )

        # exam
        try:
            self.exam = Exam.objects.get(
                id=kwargs[self.exam_url_kwarg],
                class_groups=self.class_group,
                is_active=True,
            )
        except Exam.DoesNotExist:
            messages.error(request, "آزمون مورد نظر وجود ندارد.")
            return redirect(
                reverse(
                    "exams:class-exam-list",
                    kwargs={"class_group_id": self.class_group.id},
                )
            )

        # global time window
        now = timezone.now()

        if self.exam.start_at and self.exam.start_at > now:
            messages.info(request, "آزمون هنوز شروع نشده است.")
            return redirect(
                reverse(
                    "exams:class-exam-list",
                    kwargs={"class_group_id": self.class_group.id},
                )
            )

        if self.exam.end_at and self.exam.end_at < now:
            messages.info(request, "مهلت شرکت در آزمون به پایان رسیده است.")
            logger.warning(
            "exam_permission_denied",
            extra={
                "user_id": self.request.user.id,
                "exam_id": self.exam.id,
            },
            )
            return redirect(
                reverse(
                    "exams:class-exam-list",
                    kwargs={"class_group_id": self.class_group.id},
                )
            )

        # lifecycle handling
        self.student_exam = StudentExam.objects.filter(
            student=user,
            exam=self.exam,
        ).first()

        if self.student_exam and not self.allow_existing_attempt:
            if self.student_exam.is_finished:
                logger.warning(
                "exam_permission_denied",
                extra={
                    "user_id": self.request.user.id,
                    "exam_id": self.exam.title,
                },
                )
                messages.info(request, "شما قبلاً در این آزمون شرکت کرده‌اید.")
                return redirect(
                    reverse(
                        "exams:summary",
                        kwargs={
                            "exam_id": self.exam.id,
                            "class_group_id": self.class_group.id,
                        },
                    )
                )

            messages.info(request, "آزمون شما در حال انجام است.")
            logger.warning(
                "exam_permission_denied",
                extra={
                    "user_id": self.request.user.id,
                    "exam_id": self.exam.title,
                    'message': "آزمون شما در حال انجام است."
                },
                )
            return redirect(
                reverse(
                    "exams:take",
                    kwargs={
                        "exam_id": self.exam.id,
                        "class_group_id": self.class_group.id,
                    },
                )
            )

        return super().dispatch(request, *args, **kwargs)
