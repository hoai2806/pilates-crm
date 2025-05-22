from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, HealthDocument, CustomerActivity, Appointment, CustomerPackage
from custom_admin.admin import CustomAdminMixin
from django import forms
from django.forms import SplitDateTimeWidget

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('appointment_date', 'content', 'instructors')
        widgets = {
            'appointment_date': SplitDateTimeWidget(
                date_attrs={'type': 'date'}, 
                time_attrs={'type': 'time'},
                date_format='%Y-%m-%d',
                time_format='%H:%M'
            ),
            'instructors': forms.CheckboxSelectMultiple(),
        }

class HealthDocumentInline(admin.TabularInline):
    model = HealthDocument
    extra = 1
    fields = ('document_type', 'file', 'description', 'related_payment', 'related_attendance')
    classes = ('health-documents-inline',)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            # Lọc các payment và attendance theo khách hàng
            formset.form.base_fields['related_payment'].queryset = obj.payments.all()
            # Nếu có module lớp học
            if hasattr(obj, 'attendances'):
                formset.form.base_fields['related_attendance'].queryset = obj.attendances.all()
        return formset

class CustomerActivityInline(admin.TabularInline):
    model = CustomerActivity
    extra = 1
    fields = ('content', 'timestamp')
    readonly_fields = ('timestamp',)

class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 1
    fields = ('appointment_date', 'instructors', 'content')
    readonly_fields = ('appointment_date',)

class CustomerPackageInline(admin.TabularInline):
    model = CustomerPackage
    extra = 0
    fields = ('class_type', 'total_sessions', 'remaining_sessions', 'start_date', 'end_date', 'status')
    readonly_fields = ('total_sessions',)

class CustomerAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'gender', 'status', 'source', 'registration_date', 'active')
    list_filter = ('active', 'gender', 'status', 'source', 'registration_date')
    search_fields = ('full_name', 'phone', 'address', 'parent_name', 'parent_phone')
    date_hierarchy = 'registration_date'
    
    fieldsets = (
        (None, {
            'fields': ('full_name', 'phone', 'address', 'gender', 'date_of_birth', 'emergency_contact', 'active')
        }),
        ('Thông tin chi tiết', {
            'fields': ('health_issues', 'notes', 'profile_image')
        }),
        ('Thông tin phụ huynh (nếu có)', {
            'fields': ('parent_name', 'parent_phone'),
            'classes': ('collapse',),
        }),
        ('Thông tin khách hàng', {
            'fields': ('status', 'source', 'registration_date'),
        }),
    )
    
    readonly_fields = ('registration_date',)
    
    inlines = [
        CustomerPackageInline,
        AppointmentInline,
        CustomerActivityInline,
        HealthDocumentInline,
    ]
    
    def get_status_display(self, obj):
        if obj.status == 'contact':
            return format_html('<span class="status-contact">{}</span>', obj.get_status_display())
        elif obj.status == 'trial':
            return format_html('<span class="status-trial">{}</span>', obj.get_status_display())
        elif obj.status in ['purchased', 'repurchased']:
            return format_html('<span class="status-purchased">{}</span>', obj.get_status_display())
        else:
            return format_html('<span class="status-no">{}</span>', obj.get_status_display())
    get_status_display.short_description = "Trạng thái khách hàng"
    
    class Media:
        css = {
            'all': ('css/custom_buttons.css', 'css/dashboard.css',),
        }

class AppointmentAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('customer', 'appointment_date', 'get_instructors')
    list_filter = ('appointment_date',)
    search_fields = ('customer__full_name', 'content')
    date_hierarchy = 'appointment_date'
    
    def get_instructors(self, obj):
        return ", ".join([instructor.full_name for instructor in obj.instructors.all()])
    get_instructors.short_description = "Huấn luyện viên"

class CustomerPackageAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('customer', 'class_type', 'total_sessions', 'remaining_sessions', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'class_type', 'start_date')
    search_fields = ('customer__full_name', 'notes')
    date_hierarchy = 'start_date'
    autocomplete_fields = ['customer', 'class_type', 'payment']
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'class_type', 'payment')
        }),
        ('Thông tin gói tập', {
            'fields': ('total_sessions', 'remaining_sessions', 'start_date', 'end_date', 'status')
        }),
        ('Ghi chú', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['deactivate_packages', 'activate_packages']
    
    def deactivate_packages(self, request, queryset):
        queryset.update(status='cancelled')
    deactivate_packages.short_description = "Hủy gói tập đã chọn"
    
    def activate_packages(self, request, queryset):
        queryset.update(status='active')
    activate_packages.short_description = "Kích hoạt gói tập đã chọn"

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(CustomerPackage, CustomerPackageAdmin)

@admin.register(HealthDocument)
class HealthDocumentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'document_type', 'description', 'upload_date')
    list_filter = ('document_type', 'upload_date')
    search_fields = ('customer__full_name', 'description')
    ordering = ('-upload_date',)

@admin.register(CustomerActivity)
class CustomerActivityAdmin(admin.ModelAdmin):
    list_display = ('customer', 'content', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('customer__full_name', 'content')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
