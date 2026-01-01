from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ('mobile', 'name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    search_fields = ('mobile', 'name', 'last_name')
    ordering = ('mobile',)

    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('name', 'last_name', 'role')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'mobile',
                'name',
                'last_name',
                'role',
                'password1',
                'password2',
                'is_staff',
                'is_active',
            ),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
