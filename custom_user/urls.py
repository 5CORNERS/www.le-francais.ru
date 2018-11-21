from django.conf.urls import url
from .views import SawMessageView

urlpatterns = [
	url('^/account/saw_message/$', SawMessageView.as_view(), name='saw_message')
]