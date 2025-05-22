from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

class CustomAdminMixin:
    """
    Mixin cung cấp các chức năng tùy chỉnh cho ModelAdmin
    - Thêm nút "Xem chi tiết" vào danh sách
    """
    
    def get_list_display(self, request):
        """Thêm cột action_buttons vào list_display"""
        list_display = super().get_list_display(request)
        if 'action_buttons' not in list_display:
            list_display = list(list_display) + ['action_buttons']
        return list_display
    
    def action_buttons(self, obj):
        """Hiển thị các nút hành động: Xem chi tiết, Sửa, Xóa"""
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        
        # URL cho chức năng xem chi tiết
        detail_url = reverse('custom_admin:object_detail', args=[app_label, model_name, obj.pk])
        
        # URL cho chức năng sửa và xóa
        edit_url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk])
        delete_url = reverse(f'admin:{app_label}_{model_name}_delete', args=[obj.pk])
        
        # HTML cho các nút đẹp hơn
        return format_html(
            '<div class="action-buttons">'
            '<a href="{}" class="action-btn view-btn" title="Xem chi tiết">'
            '<i class="fas fa-eye"></i></a>'
            '<a href="{}" class="action-btn edit-btn" title="Chỉnh sửa">'
            '<i class="fas fa-edit"></i></a>'
            '<a href="{}" class="action-btn delete-btn" title="Xóa">'
            '<i class="fas fa-trash"></i></a>'
            '</div>',
            detail_url, edit_url, delete_url
        )
    
    action_buttons.short_description = 'Hành động'
    action_buttons.allow_tags = True
    
    class Media:
        css = {
            'all': ('css/custom_buttons.css',)
        }
