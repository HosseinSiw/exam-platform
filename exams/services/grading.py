from django.db import transaction
from django.utils import timezone

from exams.grading.resolver import resolve_grading_policy
import logging 

logger = logging.getLogger('apps.exams')

class ExamGradingService:
    """
    Orchestrates grading process for a StudentExam.
    """

    def __init__(self, student_exam):
        self.student_exam = student_exam
        self.exam = student_exam.exam
        self.policy = resolve_grading_policy(self.exam)

    def grade(self, force=False):
        """
        Grades the exam.

        - idempotent by default
        - force=True allows re-grading
        """

        if self.student_exam.graded_at and not force:
            return

        with transaction.atomic():
            total_score = 0

            answers = (
                self.student_exam.answers
                .select_related('question', 'selected_option')
            )

            for answer in answers:
                awarded = self.policy.grade(answer)
                answer.awarded_score = awarded
                answer.save(update_fields=['awarded_score'])
                total_score += awarded

            self.student_exam.score = total_score
            self.student_exam.graded_at = timezone.now()
            self.student_exam.save(update_fields=['score', 'graded_at'])
            logger.info(
                "grading_completed",
                    extra={
                        "student_exam_id": self.student_exam.id,
                        "score": total_score,
                    },
                )