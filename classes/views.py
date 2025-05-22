from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .models import ClassTypePrice, ClassType

# Create your views here.

@login_required
@require_GET
def class_price_api(request, price_id):
    try:
        price = ClassTypePrice.objects.get(id=price_id)
        data = {
            'id': price.id,
            'class_type': price.class_type.id,
            'class_type_name': price.class_type.name,
            'class_format': price.class_format,
            'class_format_display': price.get_class_format_display(),
            'number_of_sessions': price.number_of_sessions,
            'unit_price': float(price.unit_price),
            'total_price': float(price.total_price)
        }
        return JsonResponse(data)
    except ClassTypePrice.DoesNotExist:
        return JsonResponse({'error': 'Price not found'}, status=404)

@login_required
@require_GET
def class_prices_by_type_api(request, class_type_id):
    try:
        class_type = ClassType.objects.get(id=class_type_id)
        prices = class_type.prices.all()
        
        data = []
        for price in prices:
            data.append({
                'id': price.id,
                'class_format': price.class_format,
                'class_format_display': price.get_class_format_display(),
                'number_of_sessions': price.number_of_sessions,
                'unit_price': float(price.unit_price),
                'total_price': float(price.total_price)
            })
        
        return JsonResponse(data, safe=False)
    except ClassType.DoesNotExist:
        return JsonResponse({'error': 'Class type not found'}, status=404)

@login_required
@require_GET
def class_type_api(request, class_type_id):
    try:
        class_type = ClassType.objects.get(id=class_type_id)
        data = {
            'id': class_type.id,
            'name': class_type.name,
            'description': class_type.description,
            'duration': class_type.duration,
            'max_capacity': class_type.max_capacity,
            'difficulty_level': class_type.difficulty_level,
            'class_category': class_type.class_category,
            'class_category_display': class_type.get_class_category_display(),
            'branches': list(class_type.branches.values('id', 'name'))
        }
        return JsonResponse(data)
    except ClassType.DoesNotExist:
        return JsonResponse({'error': 'Class type not found'}, status=404)
