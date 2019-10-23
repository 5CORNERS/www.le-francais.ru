from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from social_core.utils import setting_name
# from registration.backends.default.views import RegistrationView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from conjugation.sitemap import ConjugationSitemap
from forum.sitemap_generator import ForumSitemap, TopicSitemap
# from custom_user.forms import MyCustomUserForm
from home.forms import AORProfileForm
from home.urls import site_import_urls, api_urls, payment_urls, coffee_urls, \
	activate_urls, modal_urls, meta_urls, service_urls, urlpatterns as home_urls
from home.views import MovePostView, AorAddPostView, AorEditPostView, \
    AorTopicView, move_post_processing, favicon, activation_log
from home.views import change_username, \
    LeFrancaisWagtailSitemap as WagtailSitemap
from notifications import urls as notifications_api_urls
from profiles.views import UserTopics, UserPosts
from pybb.views import ProfileEditView
from search import views as search_views
from tinkoff_merchant.urls import urlpatterns as tinkoff_urls
from le_francais_dictionary.urls import urlpatterns as dictionary_urls

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''
urlpatterns = [
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^ads\.txt$', TemplateView.as_view(template_name='ads.txt', content_type='text/plain')),

    url(r'^favicon\.ico$', favicon),

    url('^sitemap\.xml$', sitemap, {'sitemaps': {
        'forum': ForumSitemap,
        'topic': TopicSitemap,
        'wagtail': WagtailSitemap,
        'conjugation': ConjugationSitemap,
    }}),

    url('^update_sitemap\.xml$',
        TemplateView.as_view(template_name='static_sitemap.xml',
                             content_type='application/xml')),

    url(r'^dictionary/', include(dictionary_urls, namespace='dictionary')),

    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^activation-log/$', activation_log, name='activation_log'),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),

    url(r'^import/', include(site_import_urls)),
    url(r'^api/', include(api_urls, namespace='api')),
    url(r'^api/', include(service_urls)),
    url(r'^api/', include(notifications_api_urls, namespace='notifications')),
    url(r'^modal/', include(modal_urls, namespace='modal')),

    url(r'^payments/', include(payment_urls, namespace='payments')),

    url(r'^home/', include(home_urls, namespace='home')),

    url(r'^coffee/', include(coffee_urls)),
    url(r'^activate/', include(activate_urls, namespace='activate')),

    url(r'^accounts/', include('custom_user.urls', namespace='custom_user')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/username/change/$', change_username, name='account_change_username'),
    url(r'^accounts/username/change_new/$', change_username, name='account_change_username'),

    url(r'^comments/', include('django_comments_xtd.urls')),

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

    url(r'^conjugaison/', include('conjugation.urls', namespace='conjugation')),


    url(r'^le_nombres/', include('le_nombres.urls')),
    url(r'^', include(meta_urls, namespace='meta')),
    url(r'^', include('social_django.urls'.format(extra), namespace='social')),
    url(r'', include('user_sessions.urls', 'user_sessions')),
    url(r'^new-users-redirect-url/', TemplateView.as_view(template_name='account/change_username_new.html')),
    url(r'^tinkoff/', include(tinkoff_urls, namespace='tinkoff_payment')),
    url(r'^', include(wagtail_urls)),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
