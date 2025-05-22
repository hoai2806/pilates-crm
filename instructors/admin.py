from django.contrib import admin
from .models import Instructor
from custom_admin.admin import CustomAdminMixin

@admin.register(Instructor)
class InstructorAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'specialties', 'active')
    list_filter = ('active', 'gender', 'hire_date')
    search_fields = ('full_name', 'email', 'phone', 'specialties')
    ordering = ('full_name',)
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('full_name', 'gender', 'date_of_birth', 'profile_image')
        }),
        ('Thông tin liên hệ', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Thông tin công việc', {
            'fields': ('bio', 'certifications', 'specialties', 'hire_date', 'weekday_hourly_rate', 'sunday_hourly_rate', 'active')
        }),
    )
