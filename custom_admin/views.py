from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.utils.text import capfirst
from django.db.models import Count
from django.urls import reverse
from django.contrib import admin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from classes.models import ClassSchedule
from customers.models import CustomerPackage

# Create your views here.

@staff_member_required
def object_detail_view(request, app_label, model_name, object_id):
    """
    View hiển thị chi tiết của một đối tượng dựa trên app_label, model_name và object_id
    """
    # Lấy model từ app_label và model_name
    model = apps.get_model(app_label, model_name)
    
    # Lấy đối tượng cần xem chi tiết
    obj = get_object_or_404(model, pk=object_id)
    
    # Lấy ModelAdmin để truy xuất thông tin fieldsets và inlines
    model_admin = admin.site._registry.get(model)
    
    # Lấy thông tin fieldsets
    if hasattr(model_admin, 'fieldsets'):
        fieldsets = model_admin.fieldsets
    else:
        fieldsets = [(None, {'fields': [f.name for f in model._meta.fields]})]
    
    # Chuẩn bị dữ liệu để hiển thị
    object_data = {}
    field_labels = {}
    number_fields = []
    
    # Lấy tên hiển thị và giá trị của các trường
    for fieldset_name, fieldset_options in fieldsets:
        for field_name in fieldset_options.get('fields', []):
            # Xử lý trường hợp field là list hoặc tuple (trong trường hợp fields)
            if isinstance(field_name, (list, tuple)):
                continue
                
            # Bỏ qua các trường là property
            if hasattr(model, field_name) and isinstance(getattr(model, field_name, None), property):
                continue
                
            try:
                field = model._meta.get_field(field_name)
                field_labels[field_name] = capfirst(field.verbose_name)
                
                # Xử lý trường đặc biệt như ForeignKey, DateField...
                if hasattr(obj, f'get_{field_name}_display'):
                    object_data[field_name] = getattr(obj, f'get_{field_name}_display')()
                else:
                    value = getattr(obj, field_name)
                    if hasattr(value, 'all') and callable(value.all):
                        # Trường ManyToMany
                        related_objects = value.all()
                        object_data[field_name] = ", ".join(str(item) for item in related_objects)
                    else:
                        object_data[field_name] = value
                        
                # Kiểm tra nếu trường này là số để định dạng phù hợp
                if field.get_internal_type() in ['DecimalField', 'FloatField', 'IntegerField']:
                    number_fields.append(field_name)
            except Exception as e:
                # Bỏ qua các trường không tồn tại hoặc gặp lỗi
                continue
    
    # Xử lý thông tin inlines nếu có
    inlines_data = []
    if hasattr(model_admin, 'inlines'):
        for inline_class in model_admin.inlines:
            inline_model = inline_class.model
            
            # Xác định fk_name đúng
            fk_name = getattr(inline_class, 'fk_name', None)
            if fk_name is None:
                # Tìm ForeignKey đầu tiên trỏ đến model chính
                for field in inline_model._meta.fields:
                    if field.get_internal_type() == 'ForeignKey' and field.related_model == model:
                        fk_name = field.name
                        break
            
            if fk_name:
                # Tạo filter là một dict với key là string
                filter_kwargs = {fk_name: obj.pk}
                inline_qs = inline_model.objects.filter(**filter_kwargs)
                
                inline_items = []
                for inline_obj in inline_qs:
                    item_data = {}
                    for field in inline_model._meta.fields:
                        if field.name == 'id':
                            continue
                        
                        # Lấy giá trị và nhãn của trường
                        field_name = field.name
                        field_label = capfirst(field.verbose_name)
                        
                        if hasattr(inline_obj, f'get_{field_name}_display'):
                            field_value = getattr(inline_obj, f'get_{field_name}_display')()
                        else:
                            field_value = getattr(inline_obj, field_name)
                            
                        # Xử lý trường ForeignKey
                        if field.get_internal_type() == 'ForeignKey' and field_value is not None:
                            field_value = str(field_value)
                        
                        item_data[field_label] = field_value
                    
                    inline_items.append(item_data)
                
                if inline_items:
                    inlines_data.append({
                        'verbose_name_plural': capfirst(inline_model._meta.verbose_name_plural),
                        'items': inline_items
                    })
    
    # Tìm và thống kê các đối tượng liên kết (related objects)
    related_objects = []
    
    # Tìm tất cả các related objects (forward and reverse relations)
    for related_object in [f for f in model._meta.get_fields() 
                          if (f.one_to_many or f.one_to_one or f.many_to_many) 
                          and f.auto_created and not f.concrete]:
        if not related_object.related_model:
            continue
            
        # Lấy queryset của related objects
        related_model = related_object.related_model
        
        # Kiểm tra nếu đây là trường related
        if hasattr(related_object, 'get_accessor_name'):
            accessor_name = related_object.get_accessor_name()
            if hasattr(obj, accessor_name):
                related_queryset = getattr(obj, accessor_name)
                # Bỏ qua nếu không phải là Manager hoặc QuerySet
                if not hasattr(related_queryset, 'all'):
                    continue
                
                # Lấy model admin nếu có
                related_model_admin = admin.site._registry.get(related_model)
                
                # Số lượng đối tượng liên kết
                count = related_queryset.count()
                
                if count > 0:
                    # Tạo URL để xem danh sách các đối tượng liên kết
                    list_url = None
                    if related_model_admin:
                        list_url = reverse(f'admin:{related_model._meta.app_label}_{related_model._meta.model_name}_changelist')
                        
                    # Tạo thông tin liên kết
                    related_objects.append({
                        'model_name': capfirst(related_model._meta.verbose_name_plural),
                        'count': count,
                        'list_url': list_url,
                        'items': list(related_queryset.all()[:10]),  # Lấy 10 item đầu tiên
                        'field_name': related_object.field.name if hasattr(related_object, 'field') else None
                    })
    
    # Chuẩn bị context cho template
    context = {
        'title': f'Chi tiết: {obj}',
        'object': obj,
        'object_data': object_data,
        'field_labels': field_labels,
        'fieldsets': fieldsets,
        'number_fields': number_fields,
        'inlines': inlines_data,
        'related_objects': related_objects,
        'opts': model._meta,
        'app_label': app_label,
        'original': obj,
        'admin_site': admin.site,
        'has_absolute_url': hasattr(obj, 'get_absolute_url'),
    }
    
    # Tích hợp admin template context
    from django.contrib.admin.views.main import IS_POPUP_VAR
    context.update({
        'add': False,
        'change': False,
        'has_add_permission': model_admin.has_add_permission(request),
        'has_change_permission': model_admin.has_change_permission(request, obj),
        'has_delete_permission': model_admin.has_delete_permission(request, obj),
        'has_view_permission': model_admin.has_view_permission(request, obj),
        'has_editable_inline_admin_formsets': False,
        'is_popup': IS_POPUP_VAR in request.GET,
        'module_name': str(model._meta.verbose_name_plural),
        'show_close': False,
    })
    
    # Thử tìm template tùy chỉnh cho model này
    template_candidates = [
        f'admin/{app_label}/{model_name}/detail.html',
        'admin/view_detail/detail.html',
    ]
    
    template = None
    for template_name in template_candidates:
        try:
            get_template(template_name)
            template = template_name
            break
        except TemplateDoesNotExist:
            continue
    
    if template is None:
        template = 'admin/view_detail/detail.html'
    
    return render(request, template, context)

@login_required
def class_session_info(request):
    """API để lấy thông tin buổi học"""
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Missing session_id parameter'}, status=400)
    
    try:
        session = ClassSchedule.objects.get(id=session_id)
        return JsonResponse({
            'id': session.id,
            'class_type_id': session.class_type_id,
            'class_type_name': session.class_type.name
        })
    except ClassSchedule.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

@login_required
def customer_packages(request):
    """API để lấy danh sách gói tập phù hợp của khách hàng"""
    customer_id = request.GET.get('customer_id')
    class_type_id = request.GET.get('class_type_id')
    
    if not customer_id or not class_type_id:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    # Lấy các gói tập còn hiệu lực và còn buổi
    packages = CustomerPackage.objects.filter(
        customer_id=customer_id,
        class_type_id=class_type_id,
        status='active',
        remaining_sessions__gt=0
    ).order_by('end_date')
    
    # Chuyển đổi sang JSON
    packages_data = []
    for pkg in packages:
        packages_data.append({
            'id': pkg.id,
            'class_type_id': pkg.class_type_id,
            'class_type_name': pkg.class_type.name,
            'total_sessions': pkg.total_sessions,
            'remaining_sessions': pkg.remaining_sessions,
            'start_date': pkg.start_date.strftime('%d/%m/%Y') if pkg.start_date else None,
            'end_date': pkg.end_date.strftime('%d/%m/%Y') if pkg.end_date else None
        })
    
    return JsonResponse(packages_data, safe=False)
