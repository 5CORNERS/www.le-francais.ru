import json
import threading
from datetime import datetime, timedelta

import httplib2
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from oauth2client.client import OAuth2WebServerFlow
from pure_pagination import Paginator, PaginationMixin
from pybb import defaults, util as pybb_util
from pybb.forms import PostForm
from pybb.models import Post, Topic
from pybb.permissions import perms
from pybb.views import AddPostView, EditPostView, TopicView
from social_core.utils import setting_name
from user_sessions.models import Session
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap as WagtailSitemap
from wagtail.core.models import Page

from home.models import PageWithSidebar, LessonPage, ArticlePage, BackUrls, DefaultPage, IndexPage
from home.src.site_import import import_content
from tinkoff_merchant.models import Payment as TinkoffPayment
from tinkoff_merchant.services import MerchantAPI
from .forms import ChangeUsername

if "mailer" in settings.INSTALLED_APPS:
	from mailer import send_mail
else:
	from django.core.mail import send_mail

flow = OAuth2WebServerFlow(
	client_id='499129759772-bqrp9ha0vfibn6t76fdgdmd87khnn2e0.apps.googleusercontent.com',
	client_secret='CRTqrmLi-116OMgpFOnYS6wH',
	scope='https://www.googleapis.com/auth/drive',
	redirect_uri='http://localhost:8000/import/authorized')

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'


class LeFrancaisWagtailSitemap(WagtailSitemap):
	def items(self):
		q = []
		q += list(ArticlePage.objects.filter(show_in_sitemap=True))
		q += list(LessonPage.objects.filter(show_in_sitemap=True))
		q += list(PageWithSidebar.objects.filter(show_in_sitemap=True))
		q += list(DefaultPage.objects.filter(show_in_sitemap=True))
		q += list(IndexPage.objects.all())
		return q


@login_required
def change_username(request):
	if request.path == '/accounts/username/change_new/':
		template_name = 'account/change_username_new.html'
	else:
		template_name = 'account/change_username.html'

	if request.method == 'POST':
		form = ChangeUsername(request.POST)
		if form.is_valid():
			user = request.user
			username = user.normalize_username(request.POST['username'])
			user.used_usernames.append({'username': user.username, 'change_datetime': datetime.utcnow()})
			user.username = username
			user.save()
			if 'next' in request.POST:
				redirect_url = request.POST['next']
			else:
				redirect_url = '/forum/profile/edit/'
			return HttpResponseRedirect(redirect_url)
		else:
			return render(request, template_name, {'form': form})

	form = ChangeUsername()
	redirect_field_value = None
	redirect_field_name = 'next'
	if 'next' in request.GET:
		redirect_field_value = request.GET['next']
	return render(
		request,
		template_name, {
			'form': form, 'redirect_field_value': redirect_field_value,
			'redirect_field_name': redirect_field_name
		}
	)


def authorize(request):
	return redirect(flow.step1_get_authorize_url())


def authorized(request):
	credentials = flow.step2_exchange(request.GET['code'])
	http = credentials.authorize(httplib2.Http())
	t = threading.Thread(
		target=import_content,
		args=(http,)
	)
	t.setDaemon(True)
	t.start()
	return HttpResponse('')


def get_navigation_object_from_page(page: Page, current_page_id: int) -> dict:
	page_object = {
		"text": str(page.title),
		"nodes": [],
		"href": page.get_url(),
		"state": {}
	}
	if isinstance(page.specific, PageWithSidebar) or isinstance(page.specific, LessonPage) or isinstance(page.specific, ArticlePage):
		menu_title = page.specific.menu_title
		if not isinstance(menu_title, str):
			menu_title = menu_title.decode()
		if menu_title != '':
			page_object["text"] = menu_title
		if not page.specific.is_selectable:
			page_object["selectable"] = False
	if page.id == current_page_id:
		page_object["state"] = {
			"selected": True
		}
		page_object["selectable"] = False
	for child in page.get_children():
		if child.show_in_menus:
			page_object["nodes"].append(get_navigation_object_from_page(child, current_page_id))
	if len(page_object["nodes"]) == 0:
		page_object.pop('nodes', None)
	return page_object


def get_nav_data(request):
	if "rootId" not in request.GET:
		return HttpResponse(status=400, content="Root page id not provided")
	root_id = request.GET['rootId']
	page_id = int(request.GET['pageId'])
	if Page.objects.get(id=root_id).show_in_menus:
		nav_items = [get_navigation_object_from_page(Page.objects.get(id=root_id), page_id)]
	else:
		nav_items = get_navigation_object_from_page(Page.objects.get(id=root_id), page_id)["nodes"]
	return HttpResponse(content=json.dumps(nav_items))


@csrf_exempt
def listen_request(request):
	lesson_number = request.POST['number'].strip()
	session_key = request.POST['key'].strip()

	try:
		session = Session.objects.get(session_key=session_key)
		lesson = LessonPage.objects.get(lesson_number=lesson_number)
	except:
		return HttpResponse('false', status=400)

	if not lesson.need_payment or not session.user.must_pay:
		return HttpResponse('full', status=200)

	if session.user is not None and lesson in session.user.payed_lessons.all() and session.ip == request.POST['ipaddress']:
		return HttpResponse('full', status=200)
	return HttpResponse('short', status=403)


def get_lesson_url(request):
	lesson_number = request.POST['lesson_number']
	return JsonResponse(dict(lesson_url='http://192.168.0.27:8080/listen.php?number=' + str(lesson_number) + '&key=' + request.session.session_key))


from .models import Payment
from .utils import message_left


class GiveMeACoffee(View):
	def post(self, request, *args, **kwargs):
		lesson_page = LessonPage.objects.get(lesson_number=request.POST['lesson_number'])
		if request.user.is_authenticated():
			if not lesson_page in request.user.payed_lessons.all():
				if request.user.cup_amount >= 1:
					try:
						cup_amount = lesson_page.add_lesson_to_user(request.user)
						send_mail(
							'Buy me a coffee',
							'{0} поблагодарил(а) вас чашечкой кофе за {1}-й урок.'.format(request.user.email, str(lesson_page.lesson_number)),
							from_email=settings.DEFAULT_FROM_EMAIL,
							recipient_list=['ilia.dumov@gmail.com']
						)
						data = dict(result="SUCCESS", description=message_left(cup_amount))
					except BaseException as e:
						data = dict(result="ERROR", description="Failed to do something: " + str(e))
				else:
					data = dict(result="ZERO_CUPS", description="У Вас закончились чашки :(")
			else:
				data = dict(result="ALREADY", description='Вы уже угощали меня за этот урок :)')
		else:
			data = dict(result="NOT_AUTH", description="Not authenticated")
		return JsonResponse(data)

	def get(self, request, *args, **kwargs):
		pass


class ActivateLesson(View):
	def post(self, request):
		lesson = LessonPage.objects.get(lesson_number=request.POST['lesson_number'])
		if request.user.is_authenticated():
			if lesson not in request.user.payed_lessons.all():
				if request.user.cup_amount >= 1 or request.user.cup_credit >= 1:
					try:
						cup_amount = lesson.add_lesson_to_user(request.user)
						send_mail(
							'Lesson Activated',
							'{0} активировал урок {1}. Осталось {2} активаций'.format(request.user.email, lesson.lesson_number, cup_amount),
							from_email=settings.DEFAULT_FROM_EMAIL,
							recipient_list=['ilia.dumov@gmail.com']
						)
						data = dict(result="SUCCESS", left=cup_amount)
					except BaseException as e:
						data = dict(result="ERROR", description="Failed to do something: " + str(e))
				else:
					data = dict(result="ZERO_CUPS")
			else:
				data = dict(result="ALREADY")
		else:
			data = dict(result="NOT_AUTH")
		return JsonResponse(data)


from django.contrib.admin.views.decorators import staff_member_required
from home.models import UserLesson


@staff_member_required
def activation_log(request):
	all = request.GET.get('all', '')
	start = -100
	if all == 'true':
		start = 0
	return render(
		request,
		template_name='home/activate_log.html',
		context={'activations': list(UserLesson.objects.filter(remains__isnull=False, user__is_staff=False, lesson__need_payment=True).order_by('date'))[start:]}
	)


from django.urls import reverse


def get_coffee_amount(request):
	return JsonResponse(dict(coffee_amount=request.user.cup_amount))


@login_required
def coffee_amount_check(request):
	if 'next' in request.GET:
		if request.user.has_coffee():
			return HttpResponseRedirect(request.GET['next'] + "?modal_open=give-me-a-coffee-modal")
		else:
			return HttpResponseRedirect(
				reverse('payments:payments') + "?next=" + request.GET['next'] + "&success_modal=give-me-a-coffee-payment-success-modal&fail_modal=give-me-a-coffee-payment-fail-modal")


from .consts import ITEMS


class TinkoffPayments(View):
	@method_decorator(login_required)
	def get(self, request):
		if request.user.saw_message and request.user.must_pay and not request.user.low_price:
			data = dict(tickets=True, cards=[
				dict(title="1 билет", image="images/ticket_1-1.png", description=None, price1="По цене стаканчика кофе в <b>McDonalds</b>", price2=68, item_id=6),
				dict(title="5 билетов", image="images/ticket_5.png", description=None, price1="по 59 ₽", price2=295, item_id=7),
				dict(title="10 билетов", image="images/ticket_10.png", description=None, price1="по 49 ₽", price2=490, item_id=8),
				dict(title="20 билетов", image="images/ticket_20.png", description=None, price1="по 39 ₽", price2=780, item_id=9),
				dict(title="50 билетов", image="images/ticket_50.png", description=None, price1="по 34 ₽", price2=1690, item_id=10),
			])
			return render(request, 'payments/tinkoff_payments_tickets.html', data)
		elif request.user.low_price:
			data = dict(tickets=True, cards=[
				dict(title="1 билет", image="images/ticket_1-39.png", description=None, price1="по 39 ₽", price2=39, item_id=11),
				dict(title="5 билет", image="images/ticket_5-39.png", description=None, price1="по 39 ₽", price2=295, item_id=12),
				dict(title="10 билет", image="images/ticket_10-39.png", description=None, price1="по 39 ₽", price2=490, item_id=13),
				dict(title="20 билет", image="images/ticket_20.png", description=None, price1="по 39 ₽", price2=780, item_id=9),
				dict(title="50 билет", image="images/ticket_50.png", description=None, price1="по 34 ₽", price2=1690, item_id=10),
			])
			return render(request, 'payments/tinkoff_payments_tickets.html', data)
		else:
			data = dict(tickets=False, cards=[
				dict(title="1 чашечка", image="images/coffee_1.png", description=None, price1="По цене стаканчика кофе в <b>McDonalds</b>", price2=68, item_id=1),
				dict(title="5 чашечек", image="images/coffee_5.png", description=None, price1="по 59 ₽", price2=295, item_id=2),
				dict(title="10 чашечек", image="images/coffee_10.png", description=None, price1="по 49 ₽", price2=490, item_id=3),
				dict(title="20 чашечек", image="images/coffee_20.png", description=None, price1="по 39 ₽", price2=780, item_id=4),
				dict(title="50 чашечек", image="images/coffee_50.png", description='''Хватит, чтобы угощать целый год.''', price1="по 34 ₽", price2=1690, item_id=5),
			])
			return render(request, 'payments/tinkoff_payments.html', data)

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		if 'item_id' in request.POST:
			item_id = int(request.POST['item_id'])
			if item_id not in ITEMS.keys():
				return HttpResponse(status=400)
			if item_id == 11 and not request.user.low_price:
				return HttpResponse(status=403)

			description = ITEMS[item_id]['description']

			payment = TinkoffPayment.objects.create(
				amount=ITEMS[item_id]['price'] * ITEMS[item_id]['quantity'], description=description, customer_key=str(request.user.id)).with_receipt(
				email=request.user.email, taxation='usn_income').with_items(
				[
					dict(
						name=ITEMS[item_id]['name'],
						price=ITEMS[item_id]['price'],
						quantity=ITEMS[item_id]['quantity'],
						amount=ITEMS[item_id]['price'] * ITEMS[item_id]['quantity'],
						category=ITEMS[item_id]['category'],
						site_quantity=ITEMS[item_id]['site_quantity'],
					)])
			payment.order_id = '{0:02d}'.format(ITEMS[item_id]['order_type_id']) + '{0:06d}'.format(payment.id)

			if "success_url" in request.POST and "fail_url" in request.POST:
				BackUrls.objects.create(
					payment=payment,
					success=request.scheme + "://" + request.META['HTTP_HOST'] + request.POST['success_url'],
					fail=request.scheme + "://" + request.META['HTTP_HOST'] + request.POST['fail_url']
				)

			tinkoff_api = MerchantAPI()
			tinkoff_api.init(payment).save()
			if payment.can_redirect():
				return JsonResponse({'payment_url': payment.payment_url, 'success': 'true'}, safe=True)
		else:
			pass


class PaymentResult(View):
	def get(self, request, *args, **kwargs):
		success = True
		if request.GET['Success'] != 'true':
			success = False
		payment = TinkoffPayment.objects.get(order_id=request.GET['OrderId'])
		try:
			back_urls = BackUrls.objects.get(payment=payment)
			success_url = back_urls.success
			fail_url = back_urls.fail
			back_urls.delete()
		except ObjectDoesNotExist:
			success_url = '/'
			fail_url = '/'
		return render(request, template_name='payments/result_page.html', context={'back_url_success': success_url, 'back_url_fail': fail_url, 'success': success, 'payment': payment})


class PaymentsView(View):
	base_template = 'payments/base_payments.html'
	success_template = 'payments/success.html'
	fail_template = 'payments/fail.html'
	proceed_template = 'payments/payments_proceed.html'

	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		data = dict(cards=[
			{'title': "1 чашечка", 'image': "images/coffee_1.png", 'description': None, 'price1': "По цене стаканчика кофе в <b>McDonalds</b>", 'cups_amount': 1, 'price2': 68},
			{'title': "5 чашечек", 'image': "images/coffee_5.png", 'description': None, 'price1': "по 59 ₽", 'cups_amount': 5, 'price2': 295},
			{'title': "10 чашечек", 'image': "images/coffee_10.png", 'description': None, 'price1': "по 49 ₽", 'cups_amount': 10, 'price2': 490},
			{'title': "20 чашечек", 'image': "images/coffee_20.png", 'description': None, 'price1': "по 39 ₽", 'cups_amount': 20, 'price2': 780},
			{'title': "50 чашечек", 'image': "images/coffee_50.png", 'description': '''Хватит, чтобы угощать целый год.''', 'price1': "по 34 ₽", 'cups_amount': 50, 'price2': 1690},
		])
		return render(request, self.base_template, data)

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		if 'cup_amount' in request.POST:
			payment = Payment.objects.create(user=request.user, cups_amount=int(request.POST['cup_amount']))
			if "success_url" in request.POST and "fail_url" in request.POST:
				params = payment.get_params(
					success_url=request.scheme + "://" + request.META['HTTP_HOST'] + request.POST['success_url'],
					fail_url=request.scheme + "://" + request.META['HTTP_HOST'] + request.POST['fail_url'])
			else:
				params = payment.get_params()
			return JsonResponse(params, safe=True)


from urllib.parse import quote
from .utils import get_signature


@method_decorator(csrf_exempt, name='dispatch')
class WlletOneNotifications(View):
	def dispatch(self, request, *args, **kwargs):
		return super(WlletOneNotifications, self).dispatch(request, *args, **kwargs)

	def get(self):
		return self.answer("Retry", "Must be POST")

	def post(self, request):
		if not 'WMI_SIGNATURE' in request.POST:
			return self.answer('Retry', "Отсутствует параметр WMI_SIGNATURE")
		if not 'WMI_PAYMENT_NO' in request.POST:
			return self.answer('Retry', "Отсутствует параметр WMI_PAYMENT_NO")
		if not 'WMI_ORDER_STATE' in request.POST:
			return self.answer('Retry', "Отсутствует параметр WMI_ORDER_STATE")

		signature = get_signature(self.get_params(request.POST)).decode('utf-8')

		payment = Payment.objects.get(id=str(request.POST["WMI_PAYMENT_NO"]))

		if signature == request.POST["WMI_SIGNATURE"]:
			if request.POST["WMI_ORDER_STATE"].upper() == "ACCEPTED":
				if not payment.status == 1:
					payment.activate_payment()
				return self.answer("Ok", "Заказ #" + request.POST["WMI_PAYMENT_NO"] + " оплачен!")
			else:
				payment.status = 3
				payment.save()
				return self.answer("Retry", "Неверное состояние " + request.POST["WMI_ORDER_STATE"])
		else:
			payment.status = 2
			payment.save()
			return self.answer("Retry", "Неверная подпись " + request.POST["WMI_SIGNATURE"])

	def answer(self, result, description):
		response = HttpResponse('WMI_RESULT=' + result + '&' + 'WMI_DESCRIPTION=' + quote(description), content_type="text/plain")
		return response

	def get_params(self, post):
		params = []
		for key, value in post.items():
			if not key == "WMI_SIGNATURE":
				params.append((key, value))
		return params


class Search(PaginationMixin, generic.ListView):
	template_name = 'search/search.html'
	paginate_by = defaults.PYBB_FORUM_PAGE_SIZE
	paginator_class = Paginator

	def dispatch(self, request, *args, **kwargs):
		self.query = request.GET.get('q')
		return super(Search, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		qs = Post.objects.all()
		if not self.query:
			return qs.none()
		for word in self.query.split()[:10]:
			qs = qs.filter(Q(body_text__icontains=word) |
			               Q(topic__name__icontains=word))
		topic_list = qs.values_list('topic', flat=True)
		return Topic.objects.filter(pk__in=topic_list)

	def get_context_data(self, **kwargs):
		context = super(Search, self).get_context_data(**kwargs)
		context['query'] = self.query
		return context


class MovePostView(TopicView):
	template_name = 'pybb/move_post_pg.html'

	def dispatch(self, request, *args, **kwargs):
		topic = Topic.objects.get(pk=kwargs['pk'])
		if not perms.may_moderate_topic(request.user, topic):
			raise PermissionDenied
		return super(MovePostView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		data = super(MovePostView, self).get_context_data()
		data['is_move'] = True
		# FIXME move to settings
		MOVE_POST_TIMEDELTA = 720
		since = datetime.today() - timedelta(days=MOVE_POST_TIMEDELTA)
		topic_qs = Topic.objects.filter(updated__gt=since)
		topic_qs = perms.filter_topics(self.request.user, topic_qs)
		data['move_to_topic_list'] = (topic_qs.select_related('forum')
		                              .order_by('forum', 'forum__name', 'name'))
		return data


class AorAddPostView(AddPostView):
	def get_form_class(self):
		return PostForm


class AorEditPostView(EditPostView):
	def get_form_class(self):
		return PostForm


class AorTopicView(TopicView):
	admin_post_form_class = PostForm


def move_post_processing(request):
	if not request.method == 'POST':
		raise PermissionDenied

	field_list = ('move_from_topic', 'move_to_topic', 'move_post_list')
	if not all(field in request.POST for field in field_list):
		# FIXME print "select at least one post"
		return redirect(request.META['HTTP_REFERER'])

	move_from_topic = request.POST.get('move_from_topic')
	move_to_topic = request.POST.get('move_to_topic')
	move_post_list = list(set(request.POST.getlist('move_post_list')))

	old_topic = Topic.objects.get(pk=move_from_topic)
	new_topic = Topic.objects.get(pk=move_to_topic)

	if (not perms.may_moderate_topic(request.user, old_topic) or
					not perms.may_moderate_topic(request.user, new_topic)):
		raise PermissionDenied

	# filter by topic for prevent access violations
	post_qs = Post.objects.filter(topic=move_from_topic, pk__in=move_post_list)
	post_qs = perms.filter_posts(request.user, post_qs)
	post_list = list(post_qs)
	post_qs.update(topic=move_to_topic)

	for post in post_list:
		if pybb_util.get_pybb_profile(post.user).autosubscribe and perms.may_subscribe_topic(post.user, new_topic):
			new_topic.subscribers.add(post.user)

	old_topic.update_counters()
	new_topic.update_counters()

	first_moved_post = Post.objects.get(pk=min(move_post_list))

	# FIXME print "success"
	return redirect(first_moved_post.get_absolute_url())


def ajax_login(request):
	form = AuthenticationForm()
	if request.method == 'POST':
		form = AuthenticationForm(None, request.POST)
		if form.is_valid():
			login(request, form.get_user())
			return HttpResponse(json.dumps({'success': 'ok'})
			                    , mimetype='application/json')
	return render(request, 'templates/ajax_login.html', {'form': form})


def ajax_registration(request):
	form = RegistrationForm()
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			return HttpResponse(json.dumps({'success': 'ok', 'mail_activation': True})
			                    , mimetype='application/json')
	return render(request, 'templates/ajax_registration.html', {'form': form})


def socialauth_success(request):
	return render(request, 'templates/socialauth_success.html', {})


def favicon(request):
	return HttpResponseRedirect(settings.STATIC_URL + 'favicon/favicon.ico')
