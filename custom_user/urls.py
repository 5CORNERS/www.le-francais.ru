from django.conf.urls import url
from . import views

urlpatterns = [
	url('^/account/saw_message/$', views.SawMessageView.as_view(), name='saw_message'),
	url('admin_commands/$', views.AdminCommands.as_view(), name='admin_commands'),
	url('update_timezone/$', views.update_timezone, name='update_timezone')
]
