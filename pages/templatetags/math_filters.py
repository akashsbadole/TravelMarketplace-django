from django import template
import math

register = template.Library()

@register.filter
def floor(value):
    """Returns the floor of a number (rounds down to nearest integer)."""
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return 0
