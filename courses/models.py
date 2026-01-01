from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


User = settings.AUTH_USER_MODEL


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teaching_courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}|{self.teacher.last_name}"


class ClassGroup(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='class_groups'
    )
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'title')
        ordering = ['course', 'title']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Enrollment(models.Model):
    student = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    class_group = models.ForeignKey(
        'courses.ClassGroup',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    enrolled_at = models.DateTimeField()
    is_active = models.BooleanField(default=True if settings.DEBUG else False)
    class Meta:
        constraints = [

            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course_enrollment'
            )
        ]
        ordering = ['-created_at']

    def clean(self):
        """
        تضمین هماهنگی Course و ClassGroup
        """
        if self.class_group.course_id != self.course_id:
            raise ValidationError(
                'کلاس انتخاب‌شده متعلق به این درس نیست.'
            )

    def save(self, *args, **kwargs):
        # avoiding save of incosistent data. 
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student} → {self.course} ({self.class_group})'
