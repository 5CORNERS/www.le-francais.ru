from django.conf.urls import url
from . import views

urlpatterns = [
	url('^unsubscribe/(?P<key>[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})', views.unsubscribe, name='unsubscribe')
]
