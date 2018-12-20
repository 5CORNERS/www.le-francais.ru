from django.conf.urls import url
from .views import SawMessageView, AdminCommands

urlpatterns = [
	url('^/account/saw_message/$', SawMessageView.as_view(), name='saw_message'),
	url('admin_commands/$', AdminCommands.as_view(), name='admin_commands'),
]
