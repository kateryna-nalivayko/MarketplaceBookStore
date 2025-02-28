from django import template
from books.models import Genre

register = template.Library()

@register.simple_tag
def tag_categories(slug):
    try:
        parent_category = Genre.objects.get(slug=slug)
        immediate_children = parent_category.children.all()
        return {
            'parent_category': parent_category,
            'immediate_children': immediate_children
        }
    except Genre.DoesNotExist:
        return {
            'parent_category': None,
            'immediate_children': None
        }
    