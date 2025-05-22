from django.contrib import admin
from django.utils.html import format_html
from .models import Branch
from custom_admin.admin import CustomAdminMixin

@admin.register(Branch)
class BranchAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'map_link', 'active')
    list_filter = ('active', 'has_elevator', 'has_wifi', 'has_parking', 'has_towel_service')
    search_fields = ('name', 'address', 'phone_number', 'description')
    fieldsets = (
        ('Thông tin chi nhánh', {
            'fields': ('name', 'address', 'phone_number', 'google_map_url', 'active'),
        }),
        ('Chi tiết bổ sung', {
            'fields': ('description', 'image'),
        }),
        ('Tiện ích - Chung', {
            'fields': ('has_elevator', 'has_wifi', 'has_lockers', 'has_shower'),
            'classes': ('collapse',),
        }),
        ('Tiện ích - Bãi đỗ xe và Di chuyển', {
            'fields': ('has_parking', 'has_bike_racks', 'has_accessible_parking'),
            'classes': ('collapse',),
        }),
        ('Tiện ích - Khác', {
            'fields': ('has_towel_service', 'has_food_drink', 'has_gender_neutral_restroom', 'has_childcare'),
            'classes': ('collapse',),
        }),
    )
    
    def map_link(self, obj):
        if obj.google_map_url:
            return format_html('<a href="{}" target="_blank">Xem trên Google Maps</a>', obj.google_map_url)
        return "-"
    map_link.short_description = "Bản đồ"
