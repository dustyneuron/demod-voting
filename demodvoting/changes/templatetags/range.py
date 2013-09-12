from django import template

register = template.Library()

@register.filter(name='range')
def range_func(value, arg=0):
    return range(int(arg), int(value))
