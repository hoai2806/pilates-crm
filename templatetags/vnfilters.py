from django import template
from django.template.defaultfilters import intcomma

register = template.Library()

@register.filter
def intdot(value):
    """Hiển thị số có dấu chấm ngăn cách hàng nghìn kiểu Việt Nam."""
    return intcomma(value).replace(',', '.') 