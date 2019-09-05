from django.conf.urls import url
from .views import get_words, add_user_words, update_user_words, \
	get_user_words, get_progress, add_packets

urlpatterns = [
	url('words/([0-9]*)/$', get_words, name='get_words'),
	url('get-words/$', get_user_words, name='get_user_words'),
	url('add-words/$', add_user_words, name='add_words'),
	url('update-words/$', update_user_words, name='update_words'),
	url('progress/$', get_progress, name='get_progress'),
	url('add-packets/$', add_packets, name='add_packets')
]
