from django.conf.urls import url

from le_francais_dictionary.views import get_repetition_words
from .views import get_words, get_progress, add_packets, update_words

urlpatterns = [
	url('words/([0-9]*)/$', get_words, name='get_words'),
	url('repetitions/$', get_repetition_words, name='get_repetitions'),
	url('update-words/$', update_words, name='update_words'),
	url('progress/$', get_progress, name='get_progress'),
	url('add-packets/$', add_packets, name='add_packets')
]
