from django.conf.urls import url
from .views import Notification, get_log, redirect_to_payment

urlpatterns = [
    url('^notification/$', Notification.as_view(), name='notification'),
    url('^log/([0-9]{4})/([0-9]{2})/$', get_log, name='get_log'),
    url('^redirect-to-payment/(?P<uuid>[^/]+)', redirect_to_payment, name='redirect_to_payment')
]
