from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def intdot2(value):
    """Hiển thị số có dấu chấm ngăn cách hàng nghìn kiểu Việt Nam (test intdot2)."""
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        value = 0
    return intcomma(value).replace(',', '.') 