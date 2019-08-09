from django.conf.urls import url
from .views import get_words

urlpatterns = [
	url('words/([0-9]*)/$', get_words, name='get_words'),
]
