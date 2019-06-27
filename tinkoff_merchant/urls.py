from django.conf.urls import url
from .views import Notification, get_log

urlpatterns = [
    url('^notification/$', Notification.as_view(), name='notification'),
    url('^log/([0-9]{4})/([0-9]{2})/$', get_log, name='get_log')
]
