from django import template
from datetime import datetime

register = template.Library()

@register.filter
def custom_date_time(value):
    value = value[:19]
    value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    value = datetime.strftime(value,"%d-%m-%Y %H:%M")
    return value