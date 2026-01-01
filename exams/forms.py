from django import forms
from django.core.exceptions import ValidationError
from .models import Exam
from courses.models import ClassGroup


class ExamAdminForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        class_groups = cleaned_data.get('class_groups')

        if course and class_groups:
            invalid_groups = class_groups.exclude(course=course)
            if invalid_groups.exists():
                raise ValidationError(
                    'تمام کلاس‌های انتخاب‌شده باید متعلق به همین درس باشند.'
                )

        return cleaned_data
    