from django import template
from django.db.models import Max, Q
from django.utils.encoding import smart_text
from django.utils.html import escape
from django.utils.safestring import mark_safe

from pybb.models import Topic

from home.utils import get_svg_avatar

register = template.Library()


@register.inclusion_tag('tags/entries.html')
def last_topics(count=50, *args, **kwargs):
	last_post_created = Max('posts__created', filter=Q(posts__on_moderation=False))
	qs = Topic.objects.filter(forum__hidden=False).filter(
		forum__category__hidden=False).prefetch_related('posts').annotate(last_post_created=last_post_created)
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
def avinit_initials(username, size=48):
	try:
		size = int(size)
	except (ValueError, TypeError):
		size = 48
	return {'svg': get_svg_avatar(username, width=str(size), height=str(size), radius=str(size/2), **{'font-size': str(size/2)})}

@register.simple_tag
def pybb_breadcrumb_link(object, anchor=''):
	url = hasattr(object, 'get_absolute_url') and object.get_absolute_url() or None
	# noinspection PyRedeclaration
	anchor = anchor or smart_text(object)
	return mark_safe('<a itemprop="item" href="%s"><span itemprop="name">%s</span></a>' % (url, escape(anchor)))


from forum.reactions import (
	get_post_reactions_summary,
	prefetch_posts_reactions,
	render_reaction_icon_html,
	get_all_reactions,
)


@register.simple_tag
def prefetch_posts_reactions_tag(post_list):
	prefetch_posts_reactions(post_list)
	return ''


@register.simple_tag
def get_post_reactions(post, current_user=None):
	return get_post_reactions_summary(post, current_user)


@register.simple_tag
def render_reaction_icon(code, css_class=''):
	return render_reaction_icon_html(code, css_class)


@register.simple_tag
def get_available_reactions():
	return get_all_reactions()

