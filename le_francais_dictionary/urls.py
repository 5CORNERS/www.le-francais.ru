from django.conf.urls import url
from .views import get_words, get_progress, add_packets, update_user_words

urlpatterns = [
	url('words/([0-9]*)/$', get_words, name='get_words'),
	url('update-words/$', update_user_words, name='update_words'),
	url('progress/$', get_progress, name='get_progress'),
	url('add-packets/$', add_packets, name='add_packets')
]
