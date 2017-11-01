from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from pybb.views import ProfileEditView
# from registration.backends.default.views import RegistrationView
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from home.views import change_username

# from custom_user.forms import MyCustomUserForm
from home.forms import AORProfileForm
from home.urls import site_import_urls, api_urls
from home.views import MovePostView, AorAddPostView, AorEditPostView, AorTopicView, move_post_processing
from profiles.views import UserTopics, UserPosts
from search import views as search_views

urlpatterns = [
	# url(r'^sitemap\.xml$', sitemap,{'sitemaps':sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
	url(r'^robots\.txt$', include('robots.urls')),

	url(r'loaderio-48b67d660cd89b42c2c95de0e8c29618/', TemplateView.as_view(template_name='loaderio-48b67d660cd89b42c2c95de0e8c29618.txt', content_type="text/plain")),

	url(r'^django-admin/', include(admin.site.urls)),
	# url(r'^login/$', auth_views.login, name='login'),
	# url(r'^logout/$', auth_views.logout, name='logout'),
	url(r'^admin/', include(wagtailadmin_urls)),
	url(r'^documents/', include(wagtaildocs_urls)),

	url(r'^search/$', search_views.search, name='search'),

	url(r'^import/', include(site_import_urls)),
	url(r'^api/', include(api_urls)),

	url(r'^accounts/', include('allauth.urls')),
	url(r'^accounts/username/change', view=change_username, name='account_change_username'),

	url(r'^captcha/', include('captcha.urls')),

	url(r'^forum/profile/edit/$', ProfileEditView.as_view(form_class=AORProfileForm), name='pybb:edit_profile'),
	url(r'^forum/users/(?P<username>[^/]+)/topics/$', UserTopics.as_view(),
		name='user_topics'),
	url(r'^forum/users/(?P<username>[^/]+)/posts/$', UserPosts.as_view(),
		name='user_posts'),

	url(r'^forum/topic/(?P<pk>\d+)/$', AorTopicView.as_view(), name='topic'),
	url(r'^forum/topic/(?P<pk>\d+)/move/$', MovePostView.as_view(), name='move_post'),
	url(r'^forum/forum/(?P<forum_id>\d+)/topic/add/$', AorAddPostView.as_view(), name='add_topic'),
	url(r'^forum/topic/(?P<topic_id>\d+)/post/add/$', AorAddPostView.as_view(), name='add_post'),
	url(r'^forum/post/(?P<pk>\d+)/edit/$', AorEditPostView.as_view(), name='edit_post'),
	url(r'^forum/post/move/processing/$', move_post_processing, name='move_post_processing'),
	url(r'^forum/', include('pybb.urls', namespace='pybb')),

	url(r'^messages/', include('forum_messages.urls')),

	url(r'^old_site/', include('old_site.urls')),

	url(r'^', include('social_django.urls', namespace='social')),
	url(r'^', include(wagtail_urls)),

]

if settings.DEBUG:
	from django.conf.urls.static import static
	from django.contrib.staticfiles.urls import staticfiles_urlpatterns

	# Serve static and media files from development server
	urlpatterns += staticfiles_urlpatterns()
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
