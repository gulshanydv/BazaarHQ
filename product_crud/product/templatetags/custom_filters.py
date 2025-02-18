# In product/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, class_name):
    """
    Adds a CSS class to a form field.
    """
    if hasattr(field, 'field'):
        field.field.widget.attrs.update({'class': class_name})
    return field

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0