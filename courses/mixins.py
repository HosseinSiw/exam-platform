from django.core.exceptions import PermissionDenied
from .models import Course, Enrollment


class StudentEnrolledRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not Enrollment.objects.filter(
            student=request.user,
            course_id=kwargs['course_id']
        ).exists():
            raise PermissionDenied("شما در این دوره آموزشی شرکت نکرده اید")

        return super().dispatch(request, *args, **kwargs)