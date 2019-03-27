import random
import re
import string

from django import template
from django.conf import settings
from pybb.models import Topic, Post

from custom_user.models import User
from home.models import IndexReviews, AdUnit
from home.models import PageLayoutAdvertisementSnippet, LessonPage, Payment
from home.utils import get_signature

register = template.Library()


@register.filter
def index(List, i):
	return List[int(i)]


@register.inclusion_tag('tags/include_advertisements.html')
def include_advertisements(contains=None):
	random_id = ''.join(
		random.choices(string.ascii_uppercase + string.digits, k=5))
	if contains:
		snippets = list(AdUnit.objects.filter(
			adunit_code__contains=contains).order_by('adunit_code'))
	return {
		'id': random_id, 'ads': snippets,
		'ids': [random_id + '-' + str(i) for i in range(len(snippets))]
	}


def safe_int(value):
	try:
		result = int(value)
	except TypeError:
		result = 0
	return result


@register.simple_tag()
def split_canonical(url):
	return url.split('==')[0]


@register.simple_tag()
def t2seconds(value):
	pattern = r'(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)'
	match = re.match(pattern, value)
	hours = safe_int(match.group('hours'))
	minutes = safe_int(match.group('minutes'))
	seconds = safe_int(match.group('seconds'))
	return hours * 3600 + minutes * 60 + seconds


@register.simple_tag(takes_context=True)
def php_listen_request(context, n):
	pass


@register.simple_tag()
def np4lesson(user: User, lesson: LessonPage):
	result = False
	if user.is_authenticated and user.must_pay and lesson.need_payment:
		result = True
	return result


@register.assignment_tag(takes_context=True)
def get_full_path(context):
	request = context['request']
	return request.build_absolute_uri().split('?')[0]


@register.assignment_tag()
def check_user_lesson(user: User, lesson: LessonPage):
	if not user.is_authenticated:
		return False
	elif lesson in user.payed_lessons.all():
		return True
	return False


@register.assignment_tag()
def get_payment_by_id(id: str):
	return Payment.objects.get(id=id)


@register.inclusion_tag('tags/payment_form.html', takes_context=True)
def payment_params(context, payment):
	merchant_id = settings.WALLET_ONE_MERCHANT_ID

	if payment.cups_amount == 1:
		payment_amount = 68
	elif payment.cups_amount == 5:
		payment_amount = 295
	elif payment.cups_amount == 10:
		payment_amount = 490
	elif payment.cups_amount == 20:
		payment_amount = 780
	elif payment.cups_amount == 50:
		payment_amount = 1690

	currency_id = u'643'  ## Russian rubles
	payment_no = payment.id
	description = "www.le-francais.ru -- Покупка " + str(
		payment.cups_amount) + " «чашек кофе»."
	success_url = "https://www.le-francais.ru/payments?success"
	fail_url = "https://www.le-francais.ru/payments?fail"
	expired_date = payment.expired_date().isoformat()
	customer_email = payment.user.email

	params = [
		('WMI_MERCHANT_ID', merchant_id),
		('WMI_PAYMENT_AMOUNT', payment_amount),
		('WMI_CURRENCY_ID', currency_id),
		('WMI_PAYMENT_NO', payment_no),
		('WMI_DESCRIPTION', description),
		('WMI_SUCCESS_URL', success_url),
		('WMI_FAIL_URL', fail_url),
		('WMI_EXPIRED_DATE', expired_date),
		('WMI_CUSTOMER_EMAIL', customer_email),
	]

	signature = get_signature(params)
	params.append(('WMI_SIGNATURE', signature))

	return {'params': params}


@register.assignment_tag()
def message(n, form1, form2, form5):
	n10 = abs(n) % 10
	n100 = abs(n) % 100
	if n10 == 1 and n100 != 11:
		return '{0} {1}'.format(str(n), form1)
	elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
		return '{0} {1}'.format(str(n), form2)
	else:
		return '{0} {1}'.format(str(n), form5)


@register.inclusion_tag('ads/topic_advert.html')
def forum_advert(counter, length):
	if counter == 0:
		return {'advert_type': 'top', 'counter': counter, 'length': length}
	if counter == length - 1 and length >= 5:
		return {'advert_type': 'bottom', 'counter': counter, 'length': length}
	if counter == length // 2 and length >= 10:
		return {'advert_type': 'middle', 'counter': counter, 'length': length}
	return {'counter': counter, 'length': length}


@register.inclusion_tag('tags/include_30_block.html', takes_context=True)
def include_30_block(context, stream_value, words_count):
	html = ''
	for block in stream_value:
		html += block.render()
	return dict(html=html, words_count=words_count)


@register.inclusion_tag('tags/advert_body.html', takes_context=True)
def page_advert_body(context, placement, page_type):
	try:
		test = dict(body=PageLayoutAdvertisementSnippet.objects.filter(
			placement=placement, page_type=page_type).exclude(live=False)[0].body)
		return dict(
			body=PageLayoutAdvertisementSnippet.objects \
				.filter(placement=placement, page_type=page_type) \
				.exclude(live=False)[0].body,
			placement=placement
		)
	except:
		return dict(body=None)


@register.inclusion_tag('tags/advert_head.html', takes_context=True)
def advert_head(context, page):
	block_list = []

	if isinstance(page, LessonPage):
		elements = [page.body, page.comments_for_lesson, page.dictionary]
		block_list = search_advertisement_heads(elements, block_list)
		for child_value in page.other_tabs:
			for block in child_value.value['body']:
				if block.block_type == 'advertisement':
					block_list.append(block.value['advertisement'].header)

	elif page.page_type == 'page_with_sidebar' or page.page_type == 'article_page':
		block_list = search_advertisement_heads([page.body], block_list)

	for layout_advert in PageLayoutAdvertisementSnippet.objects.filter(
			page_type=page.page_type).exclude(
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
		return PageLayoutAdvertisementSnippet.objects.filter(placement=placement)[
			0].head
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
		raise template.TemplateSyntaxError(
			"'%s' tag takes two arguments" % bits[0])
	value = parser.compile_filter(bits[2])
	return AssignNode(bits[1], value)


register.tag('assign', do_assign)

register.assignment_tag()
