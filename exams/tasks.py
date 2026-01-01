from celery import shared_task
from django.db import transaction
from django.utils.timezone import now
import logging

from .models import StudentExam
from .services.grading import ExamGradingService


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def grade_exam_task(self, student_exam_id):
    student_exam = StudentExam.objects.select_for_update().get(id=student_exam_id)

    logger = logging.getLogger("apps.results")
    logger.info(
        "grading_started",
        extra={"student_exam_id": student_exam_id},
    )
    if student_exam.graded_at:
        return "already_graded"

    ExamGradingService(student_exam).grade()

    student_exam.graded_at = now()
    student_exam.save(update_fields=["graded_at"])
   

    return "graded"
