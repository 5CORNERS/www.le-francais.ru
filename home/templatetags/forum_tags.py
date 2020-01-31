from django import template
from django.db.models import Max
from pybb.models import Topic

from home.utils import get_svg_avatar

register = template.Library()


@register.inclusion_tag('tags/entries.html')
def last_topics(count=50, *args, **kwargs):
	qs = Topic.objects.filter(forum__hidden=False).filter(
		forum__category__hidden=False).prefetch_related('posts').annotate(last_post_created=Max('posts__created'))
	qs = qs.filter(on_moderation=False)
	qs = qs.order_by('-last_post_created')
	qs = qs[:count]
	return dict(object_list=qs, **{'to_end': True})


@register.inclusion_tag('tags/entries.html')
def top_topics(count=50, *args, **kwargs):
	qs = Topic.objects.filter(forum__hidden=False).filter(
		forum__category__hidden=False)
	qs = qs.filter(on_moderation=False)
	qs = qs.order_by('-post_count')
	qs = qs[:count]
	return dict(object_list=qs, **{'to_end': False})


@register.inclusion_tag('pybb/_avinit.html')
def avinit_initials(username, size):
	return {'svg':get_svg_avatar(username, width=str(size), height=str(size), radius=str(size/2), **{'font-size':str(size/2)})}
