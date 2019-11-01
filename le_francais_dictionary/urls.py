from django.conf.urls import url

from le_francais_dictionary.views import get_repetition_words
from . import views
urlpatterns = [
    url('words/([0-9]*)/$', views.get_words, name='get_words'),
    url('repetitions/$', views.get_repetition_words, name='get_repetitions'),
    url('update-words/$', views.update_words, name='update_words'),
    url('progress/$', views.get_progress, name='get_progress'),
    url('progress/(?P<pk>\d+)/$', views.get_packet_progress, name='get_packet_progress'),
    url('add-packets/$', views.add_packets, name='add_packets'),
    url('clear_all/$', views.clear_all, name='clear_all'),
    url('mark-words/$', views.mark_words, name='mark_words'),
]
