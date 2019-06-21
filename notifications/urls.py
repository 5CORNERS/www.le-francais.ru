from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^get_notifications/$', get_notifications, name='get'),
    url(r'^get_new_notifications/$', get_new_notifications, name='get_new'),
    url(r'^get_new_notifications_count/$', get_new_notifications_count, name='get_new_count'),
    url(r'^get_drop_content_html/$', get_drop_content_html, name='get_drop_content_html'),
    url(r'^check_notification/(?P<pk>\d+)/$', check_notification, name='check_pk'),
    url(r'^check_notifications/$', check_notifications, name='check_list'),
]
