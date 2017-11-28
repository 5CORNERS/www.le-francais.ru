from django import template
from pybb.models import Topic

register = template.Library()


@register.inclusion_tag('tags/entries.html')
def last_topics(count=50, *args, **kwargs):
    qs = Topic.objects.filter(forum__hidden=False).filter(forum__category__hidden=False)
    qs = qs.filter(on_moderation=False)
    qs = qs.order_by('-updated','-created')
    qs = qs[:count]
    return dict(object_list=qs, **{'to_end':True})


@register.inclusion_tag('tags/entries.html')
def top_topics(count=50, *args, **kwargs):
    qs = Topic.objects.filter(forum__hidden=False).filter(forum__category__hidden=False)
    qs = qs.filter(on_moderation=False)
    qs = qs.order_by('-post_count')
    qs = qs[:count]
    return dict(object_list=qs, **{'to_end':False})
