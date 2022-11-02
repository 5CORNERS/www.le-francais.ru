import random
import re
import string
from typing import List

from django import template
from django.conf import settings

from custom_user.models import User
from home.models import IndexReviews, AdUnit
from home.models import PageLayoutAdvertisementSnippet, LessonPage, Payment
from home.utils import get_signature, files_le_francais_url, \
	is_gpt_disabled
from pybb.models import Topic, Post

register = template.Library()

@register.filter
def div(value, arg):
	"""
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    """
	try:
		value = int(value)
		arg = int(arg)
		if arg:
			return value / arg
	except:
		pass
	return ''


@register.filter
def index(List, i):
	return List[int(i)]


@register.inclusion_tag('tags/include_advertisements.html', takes_context=True)
def include_advertisements(context, contains=None, page_type=None, placement=None, in_house=False, maskable=False, is_sidebar=True):
	if maskable and context.get("hide") == True:
		return {'hide':True}
	random_id = ''.join(
		random.choices(string.ascii_uppercase + string.digits, k=5))
	snippets = AdUnit.objects.all().order_by('adunit_code')
	if contains:
		snippets = snippets.filter(adunit_code__contains=contains)
	if page_type:
		snippets = snippets.filter(page_type=page_type)
	if placement:
		snippets = snippets.filter(placement=placement)
	if in_house:
		try:
			snippets = list(snippets)
			snippets.insert(1, AdUnit.objects.get(placement='in_house_sidebar', page_type=page_type))
		except:
			pass
	return {
		'gpt_disabled': is_gpt_disabled(context.request),
		'id': random_id, 'ads': snippets,
		'mappings': list(set(ad.size_mapping for ad in snippets)),
		'ids': [random_id + '-' + str(i) for i in range(len(snippets))],
		'hide': False,
		'is_sidebar': is_sidebar,
		'request': context.get('request')
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
def get_prev_lesson(lesson_number):
	q = LessonPage.objects.filter(lesson_number__lt=lesson_number).order_by(
		'-lesson_number')
	if q.exists():
		return q.first()
	return None


@register.assignment_tag()
def get_next_lesson(lesson_number):
	q = LessonPage.objects.filter(lesson_number__gt=lesson_number).order_by(
		'lesson_number')
	if q.exists():
		return q.first()
	return None


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
		payment_amount = 78
	elif payment.cups_amount == 5:
		payment_amount = 345
	elif payment.cups_amount == 10:
		payment_amount = 590
	elif payment.cups_amount == 20:
		payment_amount = 980
	elif payment.cups_amount == 50:
		payment_amount = 1950

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
		snippet = PageLayoutAdvertisementSnippet.objects.filter(placement=placement, page_type=page_type).exclude(live=False).first()
		return dict(
			body=snippet.body,
			placement=placement,
			snippet=snippet,
			gpt_disabled=context.get('is_gpt_disabled'),
			request=context.get('request'),
			utm_source=f"{snippet.name}@{context.get('request').path}"
		)
	except:
		return dict(body=None)


@register.inclusion_tag('tags/advert_head.html', takes_context=True)
def advert_head(context, page):
	block_list = []

	if isinstance(page, LessonPage):
		if context['lesson_was_payed_by_user']:
			return {'block_list': []}
		elements = [page.body, page.comments_for_lesson, page.dictionary]
		block_list = search_advertisement_heads(elements, block_list)
		for child_value in page.other_tabs:
			for block in child_value.value['body']:
				if block.block_type == 'advertisement':
					block_list.append(block.value['advertisement'].header)

	elif page.page_type == 'page_with_sidebar' or page.page_type == 'article_page':
		block_list = search_advertisement_heads([page.body], block_list)

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

@register.inclusion_tag("tags/random_sidebar_review.html")
def random_sidebar_review():
	r = IndexReviews.objects.filter(show_in_sidebar=True).order_by('?').first()
	return {"review": r}

@register.inclusion_tag("tags/unwrap.html", takes_context=True)
def unwrap(context, blocks):
	return dict(blocks=blocks, context=context)


@register.inclusion_tag('tags/random_reviews.html')
def random_review():
	qs: List[IndexReviews] = list(IndexReviews.objects.order_by('?')) 
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

def get_shortest_title(page):
	try:
		if page.specific.menu_title:
			return page.specific.menu_title
		else:
			return page.title
	except:
		return page.title

def get_page_url(page, context):
	try:
		current_site = context['request'].site
	except (KeyError, AttributeError):
		# request.site not available in the current context; fall back on page.url
		return page.url
	return page.relative_url(current_site, request=context.get('request'))

@register.inclusion_tag('tags/breadcrumb.html', takes_context=True)
def breadcrumb(context, calling_page):
	current_page = calling_page
	pages = [current_page]
	while current_page.get_parent():
		current_page = current_page.get_parent()
		pages.append(current_page)
	pages.pop(-1)
	breadcrumbs = []
	for page in reversed(pages):
		if hasattr(page.specific, 'menu_title') and page.specific.menu_title:
			title = page.specific.menu_title
		else:
			title = page.title
		if hasattr(page.specific, 'is_selectable') and page.specific.is_selectable:
			try:
				current_site = context['request'].site
				url = page.relative_url(current_site, context['request'])
			except (KeyError, AttributeError):
				url = page.url

			breadcrumbs.append({
				'name': title,
				'url': url,
				'active': page.url == calling_page.url
			})
		else:
			breadcrumbs[-1]['name'] = f'{breadcrumbs[-1]["name"]} ({title})'
	return {
		'breadcrumbs': breadcrumbs,
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

@register.inclusion_tag('tags/payment_card.html', takes_context=False)
def payment_card(card, n):
	return dict(card=card, n=n)

register.simple_tag(files_le_francais_url, False, 'files_le_francais_url')
