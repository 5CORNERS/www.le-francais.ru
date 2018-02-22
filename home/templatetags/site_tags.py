from django import template
from pybb.models import Topic, Post

from home.models import IndexReviews
from home.models import PageLayoutAdvertisementSnippet

register = template.Library()


@register.inclusion_tag('tags/advert_body.html', takes_context=True)
def page_advert_body(context, placement, page_type):
    try:
        test = dict(body=PageLayoutAdvertisementSnippet.objects\
                .filter(placement=placement, page_type=page_type)\
                .exclude(live=False)[0].body)
        return dict(
            body=PageLayoutAdvertisementSnippet.objects\
                .filter(placement=placement, page_type=page_type)\
                .exclude(live=False)[0].body
        )
    except:
        return dict(body=None)


@register.inclusion_tag('tags/advert_head.html', takes_context=True)
def advert_head(context, page):
    block_list = []

    if page.page_type == 'lesson_page':
        elements = [page.body, page.comments_for_lesson, page.dictionary]
        block_list = search_advertisement_heads(elements, block_list)
        for child_value in page.other_tabs:
            for block in child_value.value['body']:
                if block.block_type == 'advertisement':
                    block_list.append(block.value['advertisement'].header)

    elif page.page_type == 'page_with_sidebar' or page.page_type == 'article_page':
        block_list = search_advertisement_heads([page.body], block_list)

    for layout_advert in PageLayoutAdvertisementSnippet.objects.filter(page_type=page.page_type).exclude(
            placement='none').exclude(live=False):
        for block in layout_advert.head:
            block_list.append(block.value)
        block_list = search_advertisement_heads([layout_advert.body], block_list)
    return dict(block_list=block_list)


def search_advertisement_heads(page_elements: list, list):
    for element in page_elements:
        for block in element:
            if block.block_type == 'advertisement':
                list.append(block.value['advertisement'].header)
    return list


@register.assignment_tag()
def sidebar_adverisement_head(placement):
    try:
        return PageLayoutAdvertisementSnippet.objects.filter(placement=placement)[0].head
    except:
        return None


@register.inclusion_tag("tags/advertisement.html", takes_context=True)
def advertisement_inline(context, name, header, body):
    dict = {
        'name': name,
        'header': header,
        'body': body,
    }
    return dict


@register.assignment_tag()
def get_reviews():
    return IndexReviews.objects.all()


@register.inclusion_tag("tags/unwrap.html", takes_context=True)
def unwrap(context, blocks):
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
