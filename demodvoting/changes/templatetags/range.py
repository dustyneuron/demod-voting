from django import template

register = template.Library()

@register.filter(name='range')
def range_func(value):
    return range(int(value))
