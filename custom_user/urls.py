from django.conf.urls import url
from .views import SawMessageView

urlpatterns = [
	url('^/account/saw_message/$', SawMessageView, name='saw_message')
]