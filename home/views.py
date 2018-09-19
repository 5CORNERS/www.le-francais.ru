import json
import threading
from datetime import datetime, timedelta

import httplib2
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
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
from pybb import defaults
from pybb.forms import PostForm
from pybb.models import Post, Topic
from pybb.permissions import perms
from pybb.views import AddPostView, EditPostView, TopicView
from social_core.utils import setting_name
from user_sessions.models import Session
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap as WagtailSitemap
from wagtail.core.models import Page

from home.models import PageWithSidebar, LessonPage, ArticlePage
from home.src.site_import import import_content
from .forms import ChangeUsername

flow = OAuth2WebServerFlow(client_id='499129759772-bqrp9ha0vfibn6t76fdgdmd87khnn2e0.apps.googleusercontent.com',
                           client_secret='CRTqrmLi-116OMgpFOnYS6wH',
                           scope='https://www.googleapis.com/auth/drive',
                           redirect_uri='http://localhost:8000/import/authorized')

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'


class LeFrancaisWagtailSitemap(WagtailSitemap):
    def items(self):
        return (
            self.site
                .root_page
                .get_descendants(inclusive=True)
                .live()
                .public()
                .order_by('path')) \
            .exclude(defaultpage__show_in_sitemap=False) \
            .exclude(articlepage__show_in_sitemap=False) \
            .exclude(pagewithsidebar__show_in_sitemap=False) \
            .exclude(lessonpage__show_in_sitemap=False)


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
    return render(request, template_name, {'form': form, 'redirect_field_value': redirect_field_value,
                                           'redirect_field_name': redirect_field_name})


def authorize(request):
    return redirect(flow.step1_get_authorize_url())


def authorized(request):
    credentials = flow.step2_exchange(request.GET['code'])
    http = credentials.authorize(httplib2.Http())
    t = threading.Thread(target=import_content,
                         args=(http,))
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
    if isinstance(page.specific, PageWithSidebar) or isinstance(page.specific, LessonPage) or isinstance(page.specific,
                                                                                                         ArticlePage):
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
    lesson_number = request.POST['number']
    session_key = request.POST['key']

    try:
        session = Session.objects.get(session_key=session_key)
        lesson = LessonPage.objects.get(lesson_number=lesson_number)
    except:
        return HttpResponse('false')

    if not session.user==None and session.user.must_pay:
        if lesson in session.user.payed_lessons:
            return HttpResponse('true')
        else:
            return HttpResponse('false')
    else:
        return HttpResponse('true')


from .models import Payment
from django.contrib.admin.views.decorators import staff_member_required
from .utils import message_left

class GiveMeACoffee(View):
    def post(self, request, *args, **kwargs):
        lesson_page = LessonPage.objects.get(lesson_number=request.POST['lesson_number'])
        if request.user.is_authenticated():
            if request.user.cup_amount >= 1:
                try:
                    cup_amount = lesson_page.add_lesson_to_user(request.user)
                    data = dict(result=True, description=message_left(cup_amount))
                except BaseException as e:
                    data = dict(result=False, description="Failed to do something: " + str(e))
            else:
                data = dict(result=False, description="Чтобы чем-то угощать, надо это что-то иметь :)")
        else:
            data = dict(result=False, description="Not authenticated")
        return JsonResponse(data)

    def get(self, request, *args, **kwargs):
        pass


from django.urls import reverse


@login_required
def coffee_amount_check(request):
    if 'next' in request.GET:
        if request.user.has_coffee():
            return HttpResponseRedirect(request.GET['next'] + "?modal_open=buy-me-a-coffee-modal")
        else:
            return HttpResponseRedirect(reverse('payments') + "?next=" + request.GET['next'])


@method_decorator(staff_member_required, name='dispatch')
class PaymentsView(View):
    base_template = 'payments/base_payments.html'
    success_template = 'payments/success.html'
    fail_template = 'payments/fail.html'
    proceed_template = 'payments/payments_proceed.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        if 'success' in request.GET:
            return render(request, self.success_template)
        if 'fail' in request.GET:
            return render(request, self.fail_template)
        data = dict(cards=[
            ("1 чашечка", "images/coffee_1.png", '''По цене стаканчика кофе в McDonalds''', 68, 1),
            ("5 чашечек", "images/coffee_5.png", '''59₽ за чашечку''', 295, 5),
            ("10 чашечек", "images/coffee_10.png", '''49₽ за чашечку''', 490, 10),
            ("20 чашечек", "images/coffee_20.png", '''39₽ за чашечку''', 780, 20),
            ("50 чашечек", "images/coffee_50.png", '''34₽ за чашечку — хватит на год.''', 1690, 50),
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
    post_qs.update(topic=move_to_topic)

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
