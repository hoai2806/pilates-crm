from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def remove_param(query_string, param_to_remove):
    if not query_string:
        return ""
    params = query_string.split('&')
    # Lọc ra các param không phải là param_to_remove và cũng không phải là rỗng sau khi strip
    filtered_params = [p for p in params if p.strip() and not p.startswith(param_to_remove + '=')]
    return '&amp;'.join(filtered_params) # Sử dụng &amp; cho HTML context 