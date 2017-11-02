import json
import threading
from datetime import datetime, timedelta

import httplib2
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import generic
from oauth2client.client import OAuth2WebServerFlow
from pure_pagination import Paginator, PaginationMixin
from pybb import defaults
from pybb.forms import PostForm
from pybb.models import Post, Topic
from pybb.permissions import perms
from pybb.views import AddPostView, EditPostView, TopicView
from wagtail.wagtailcore.models import Page

from home.models import PageWithSidebar, LessonPage
from home.src.site_import import import_content
from .forms import ChangeUsername

flow = OAuth2WebServerFlow(client_id='499129759772-bqrp9ha0vfibn6t76fdgdmd87khnn2e0.apps.googleusercontent.com',
                           client_secret='CRTqrmLi-116OMgpFOnYS6wH',
                           scope='https://www.googleapis.com/auth/drive',
                           redirect_uri='http://localhost:8000/import/authorized')


@login_required
def change_username(request):
	template_name = 'account/change_username.html'
	if request.method == 'POST':
		form = ChangeUsername(request.POST)
		if form.is_valid():
			user = request.user
			username = user.normalize_username(request.POST['username'])
			user.used_usernames.append({'username':user.username, 'change_datetime':datetime.utcnow()})
			user.username = username
			user.save()
			return HttpResponseRedirect('/forum/profile/edit')
		else:
			return render(request, template_name, {'form': form})
	form = ChangeUsername()
	return render(request, template_name, {'form': form})


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
	if isinstance(page.specific, PageWithSidebar) or isinstance(page.specific, LessonPage):
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
		MOVE_POST_TIMEDELTA = 60
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
