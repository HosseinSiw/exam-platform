from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(unique=True, max_length=11, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    is_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['name', 'last_name']
    
    TEACHER = 'teacher'
    STUDENT = 'student'

    ROLE_CHOICES = (
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT
    )
    
    objects = UserManager()
    def __str__(self):
        if self.role == "teacher":
            return f'{self.name} | {self.last_name}'
        else:
            return f'{self.mobile}'
    

    def is_teacher(self):
        return self.role == self.TEACHER

    def is_student(self):
        return self.role == self.STUDENT