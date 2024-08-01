from django import template


register = template.Library()


@register.simple_tag
def app_title():
    return "ESender"
