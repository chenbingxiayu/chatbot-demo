from datetime import datetime
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def mask(value: str) -> str:
    array = list(value)
    array[4:8] = 'xxxx'
    return ''.join(array)


@register.filter
def duration(time: datetime, now: datetime) -> str:
    diff = now - time
    if diff.days < 0:
        # return '' if <time> is in the future
        return ""
    s = diff.seconds
    return f"{s // 60 // 60:02d}:{s // 60 % 60 :02d}:{s % 60:02d}"
