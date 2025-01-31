from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter
def is_in_group(user, group_name):
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()