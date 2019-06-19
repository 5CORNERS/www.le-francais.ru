from django.conf.urls import url
from .views import *

notifications_api = [
    url(r'^get_notifications/$', get_notifications, name='get'),
    url(r'^check_notification/(?P<pk>\d+)/$', check_notification, name='check_pk'),
    url(r'^check_notifications/', check_notifications, name='check_list')
]
