from django.contrib import admin
from django.utils.html import format_html
from django.forms import CheckboxSelectMultiple
from django import forms
from .models import ClassType, ClassTypePrice, ClassSchedule, Attendance, CustomerPackage
from custom_admin.admin import CustomAdminMixin

class BranchCheckboxSelectMultiple(CheckboxSelectMultiple):
    class Media:
        css = {
            'all': ('css/custom_admin.css?v=2',),
        }
        js = ('js/branch_select.js?v=1',)

class ClassTypePriceInline(admin.TabularInline):
    model = ClassTypePrice
    extra = 1
    verbose_name = "Bảng giá"
    verbose_name_plural = "Bảng giá"
    fields = ('class_format', 'number_of_sessions', 'unit_price', 'get_total_price')
    readonly_fields = ('get_total_price',)
    
    def get_total_price(self, obj):
        if obj.id and obj.unit_price and obj.number_of_sessions:
            return format_html('<span class="price">{}</span>', obj.total_price)
        return '-'
    get_total_price.short_description = "Thành tiền"
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'unit_price':
            formfield.widget.attrs.update({'class': 'price-input'})
        return formfield

class ClassTypeAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'get_class_category_display', 'duration', 'max_capacity', 'difficulty_level', 'get_branches')
    list_filter = ('class_category', 'difficulty_level', 'branches')
    search_fields = ('name', 'description')
    inlines = [ClassTypePriceInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'class_category')
        }),
        ('Chi tiết', {
            'fields': ('duration', 'max_capacity', 'difficulty_level', 'branches')
        }),
    )
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'branches':
            kwargs['widget'] = BranchCheckboxSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_branches(self, obj):
        return ", ".join([branch.name for branch in obj.branches.all()])
    get_branches.short_description = "Chi nhánh"
    
    def get_class_category_display(self, obj):
        return obj.get_class_category_display()
    get_class_category_display.short_description = "Loại lớp"
    
    class Media:
        css = {
            'all': ('css/custom_admin.css?v=3',),
        }
        js = ('js/branch_select.js?v=2', 'js/price_format.js?v=1',)

class ClassTypePriceAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('class_type', 'class_format', 'number_of_sessions', 'unit_price', 'get_total_price')
    list_filter = ('class_format', 'class_type')
    search_fields = ('class_type__name',)
    autocomplete_fields = ['class_type']
    
    def get_total_price(self, obj):
        return format_html('<span class="price">{}</span>', obj.total_price)
    get_total_price.short_description = "Thành tiền"

class ClassScheduleAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'class_type', 'instructor', 'get_schedule_date_display', 'start_time', 'end_time', 'room', 'status', 'active')
    list_filter = ('active', 'class_type', 'instructor', 'is_recurring', 'day_of_week', 'status', 'specific_date')
    search_fields = ('class_type__name', 'instructor__name', 'room', 'notes')
    autocomplete_fields = ['class_type', 'instructor', 'parent_schedule']
    date_hierarchy = 'specific_date'
    change_list_template = 'admin/classes/classschedule/change_list.html'
    
    def get_schedule_date_display(self, obj):
        if obj.specific_date:
            return obj.specific_date.strftime("%d/%m/%Y")
        return obj.get_day_of_week_display()
    get_schedule_date_display.short_description = "Ngày"
    
    def get_fieldsets(self, request, obj=None):
        # Nếu là buổi học cụ thể (có specific_date)
        if obj and obj.specific_date:
            return (
                (None, {
                    'fields': ('parent_schedule', 'class_type', 'instructor', 'specific_date', 
                               'start_time', 'end_time', 'room', 'status', 'active')
                }),
                ('Chi tiết buổi học', {
                    'fields': ('actual_start_time', 'actual_end_time', 'notes'),
                }),
            )
        # Nếu là lịch học
        return (
            (None, {
                'fields': ('class_type', 'instructor', 'day_of_week', 'start_time', 'end_time', 'room', 'active')
            }),
            ('Lịch lặp lại', {
                'fields': ('is_recurring', 'recurring_days', 'start_date', 'end_date'),
                'classes': ('collapse',),
                'description': ('Cài đặt lịch lặp lại cho lớp cố định')
            }),
        )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.parent_schedule:
            return ('parent_schedule',)
        return []
    
    class Media:
        css = {
            'all': ('css/modern_timepicker.css',),
        }
        js = ('js/modern_timepicker.js', 'js/class_schedule_admin.js',)

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1
    autocomplete_fields = ['customer']

class AttendanceAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('class_session', 'customer', 'attended', 'time_in', 'time_out', 'customer_package', 'is_session_deducted')
    list_filter = ('attended', 'class_session__specific_date', 'is_session_deducted')
    search_fields = ('customer__full_name', 'class_session__class_type__name', 'notes')
    autocomplete_fields = ['customer', 'class_session', 'customer_package']
    readonly_fields = ('is_session_deducted',)
    
    fieldsets = (
        (None, {
            'fields': ('class_session', 'customer', 'attended')
        }),
        ('Thời gian', {
            'fields': ('time_in', 'time_out')
        }),
        ('Thông tin gói tập', {
            'fields': ('customer_package', 'is_session_deducted')
        }),
        ('Ghi chú', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Nếu đang thêm mới, tự động lọc danh sách gói tập phù hợp với khách hàng và loại lớp
        if not obj and 'customer' in form.base_fields and 'class_session' in form.base_fields and 'customer_package' in form.base_fields:
            class PackageChoiceField(forms.ModelChoiceField):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.queryset = self.queryset.none()
            
            form.base_fields['customer_package'] = PackageChoiceField(
                queryset=CustomerPackage.objects.all(),
                required=False,
                label="Gói tập sử dụng"
            )
            
            # Thêm JavaScript để lấy gói tập phù hợp khi chọn khách hàng và buổi học
            class Media:
                js = ('js/attendance_admin.js',)
            
            form.Media = Media
            
        return form

admin.site.register(ClassType, ClassTypeAdmin)
admin.site.register(ClassTypePrice, ClassTypePriceAdmin)
admin.site.register(ClassSchedule, ClassScheduleAdmin)
admin.site.register(Attendance, AttendanceAdmin)
