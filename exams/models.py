from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone


class GradingPolicy(models.TextChoices):
    NO_NEGATIVE = 'no_negative', 'بدون نمره منفی'
    NEGATIVE_3 = 'negative_3', 'نمره منفی (۳ غلط = ۱ صحیح)'
    NEGATIVE_5 = 'negative_5', 'نمره منفی (۵ غلط = ۱ صحیح)'


class Exam(models.Model):
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='exams'
    )

    class_groups = models.ManyToManyField(
        'courses.ClassGroup',
        related_name='exams'
    )
    grading_policy = models.CharField(
        max_length=20,
        choices=GradingPolicy.choices,
        default=GradingPolicy.NO_NEGATIVE,
        help_text='سیاست محاسبه درصد'
    )

    title = models.CharField(max_length=255, help_text='عنوان آزمون')
    description = models.TextField(blank=True, help_text='توضیحات بیشتر')

    duration_minutes = models.PositiveIntegerField(
        help_text='مدت زمان آزمون (دقیقه)'
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_at']

    def __str__(self):
        return f'{self.title} ({self.course})'


class Question(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    text = models.TextField()

    score = models.PositiveIntegerField(default=1)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'سوال'
        verbose_name_plural = 'سوالات'

    def __str__(self):
        return f'Q{self.order} - {self.exam.title}'


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )

    text = models.CharField(max_length=255)

    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # فقط یک پاسخ صحیح برای هر سوال
            models.UniqueConstraint(
                fields=['question'],
                condition=Q(is_correct=True),
                name='unique_correct_option_per_question'
            )
        ]

    # def clean(self):
    #     if self.question.options.count() >= 4 and not self.pk:
    #         raise ValidationError('هر سوال فقط ۴ گزینه دارد.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text


class StudentExam(models.Model):
    student = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='student_exams',
        limit_choices_to={'role': 'student'}
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='student_exams'
    )

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    score = models.FloatField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        constraints = [
            # هر دانش‌آموز فقط یک‌بار وارد یک آزمون
            models.UniqueConstraint(
                fields=['student', 'exam'],
                name='unique_student_exam'
            )
        ]
    def finish(self):
        """
        Marks the exam as finished (idempotent).
        """
        if not self.finished_at:
            self.finished_at = timezone.now()
            self.save(update_fields=['finished_at'])

    @property
    def is_finished(self):
        return self.finished_at is not None
    
    def __str__(self):
        return f'{self.student} - {self.exam}'
    
    def percentage(self):
        if self.score is None:
            return None

        max_score = self.exam.questions.count()
        return round((self.score / max_score) * 100, 2)

class Answer(models.Model):
    student_exam = models.ForeignKey(
        StudentExam,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_option = models.ForeignKey(
        QuestionOption,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    is_correct = models.BooleanField(default=False)

    # ✅ خروجی grading
    awarded_score = models.FloatField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student_exam', 'question'],
                name='unique_answer_per_question'
            )
        ]

    def clean(self):
        if self.selected_option and \
           self.selected_option.question_id != self.question_id:
            raise ValidationError('گزینه انتخابی متعلق به این سوال نیست.')

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.selected_option:
            self.is_correct = self.selected_option.is_correct
        else:
            self.is_correct = False
        super().save(*args, **kwargs)