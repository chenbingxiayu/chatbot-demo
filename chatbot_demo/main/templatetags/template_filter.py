from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def mask(value: str) -> str:
    array = list(value)
    array[4:8] = 'xxxx'
    return ''.join(array)
