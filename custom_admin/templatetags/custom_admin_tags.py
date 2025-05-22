from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Lấy item từ dictionary với key cho trước
    """
    return dictionary.get(key)

@register.filter 
def split(value, delimiter):
    """
    Split string by delimiter
    """
    return value.split(delimiter)

@register.filter
def trim(value):
    """
    Trim whitespace
    """
    return value.strip()

@register.filter
def startswith(value, arg):
    """
    Check if value startswith arg
    """
    return value.startswith(arg)

@register.filter
def get_app_label(obj):
    """
    Lấy app_label của đối tượng
    """
    try:
        return obj._meta.app_label
    except (AttributeError, TypeError):
        # Trường hợp obj là string hoặc không có _meta
        return str(obj)

@register.filter
def get_model_name(obj):
    """
    Lấy model_name của đối tượng
    """
    try:
        return obj._meta.model_name
    except (AttributeError, TypeError):
        # Trường hợp obj là string hoặc không có _meta
        return str(obj)

@register.filter
def get_pk(obj):
    """
    Lấy primary key của đối tượng
    """
    try:
        return obj.pk
    except (AttributeError, TypeError):
        # Trường hợp obj là string hoặc không có pk
        return str(obj)

@register.filter
def to_str(value):
    """
    Chuyển đối tượng thành chuỗi
    """
    return str(value)

@register.filter
def to_length(value):
    """
    Trả về độ dài của chuỗi hoặc đối tượng sau khi chuyển thành chuỗi
    """
    return len(str(value))

@register.filter
def is_model_object(value):
    """
    Kiểm tra xem đối tượng có phải là model object hay không
    """
    try:
        return hasattr(value, '_meta')
    except:
        return False 