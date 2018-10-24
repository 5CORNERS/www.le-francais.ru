from django.conf.urls import url
from .views import Notification

urlpatterns = [
    url('^notification/$', Notification.as_view(), name='notification'),
]
