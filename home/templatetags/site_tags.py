from django import template
from pybb.models import Topic, Post
from pybb.forms import PostForm
from home.models import IndexReviews

register = template.Library()


@register.inclusion_tag("tags/unwrap.html", takes_context=True)
def unwrap(context,blocks):
    return dict(blocks=blocks, context=context)


@register.inclusion_tag('tags/random_reviews.html')
def random_review(count=3):
    qs = IndexReviews.objects.order_by('?')
    qs = qs[:count]
    return dict(object_list=qs)


@register.inclusion_tag('tags/topic_block.html', takes_context=True)
def topic_block(context, topic_id):
    request = context.dicts[1]['context']['request']
    topic = Topic.objects.get(id=topic_id)
    queryset = Post.objects.filter(topic=topic)
    queryset.order_by('created')
    return {'topic': topic,
            'first_post': topic.head,
            'paginator': None,
            'page_obj': None,
            'is_paginated': False,
            'post_list': queryset,
            'request': request
            }


@register.inclusion_tag('tags/related_post.html')
def post_block(post_id):
    post = Post.objects.get(id=post_id)
    return {'post': post}


@register.assignment_tag(takes_context=True)
def get_site_root(context):
    return context['request'].site.root_page


@register.inclusion_tag('tags/sidebar_menu.html', takes_context=True)
def sidebar_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().filter(
        live=True,
        show_in_menus=True
    )
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.inclusion_tag('tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().filter(
        live=True,
        show_in_menus=True
    )
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
        'user': context['user']
    }


@register.inclusion_tag('tags/breadcrumb.html', takes_context=True)
def breadcrumb(context, calling_page):
    breadcrumb_pages = []
    breadcrumb_page = calling_page
    while breadcrumb_page.get_parent() is not None:
        breadcrumb_pages.append(breadcrumb_page)
        breadcrumb_page = breadcrumb_page.get_parent()
    return {
        'calling_page': calling_page,
        'breadcrumb_pages': reversed(breadcrumb_pages),
        'request': context['request'],
    }


class AssignNode(template.Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''


def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.

    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}

    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)


register.tag('assign', do_assign)
