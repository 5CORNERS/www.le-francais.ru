from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    return context['request'].site.root_page


@register.inclusion_tag('tags/menu.html', takes_context=True)
def menu(context, parent):
    menuitems = parent.get_children().filter(
        live=True,
        show_in_menus=True
    )
    return {
        'menuitems': menuitems,
        'request': context['request'],
    }
