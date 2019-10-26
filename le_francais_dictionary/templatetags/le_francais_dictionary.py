from django import template

register = template.Library()


@register.inclusion_tag('dictionary/dictionary.html')
def include_dictionary():
    return
