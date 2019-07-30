from django.conf.urls import url
from .views import *

urlpatterns = [
	url('words/([0-9]*)/$', get_words, name='get_words'),
	url('words_alt/([0-9]*)/', get_words_alt, name='get_words_alt'),
]
