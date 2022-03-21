from django.conf.urls import url

from le_francais_dictionary.views import get_repetition_words
from . import views
urlpatterns = [
    url('^words/([0-9]+)/$', views.get_words, name='get_words'),
    url('^repeat-words/$', views.get_repetition_words, name='get_repetitions'),
    url('^repeat-words/count/$', views.get_repetition_words_count, name='get_repetitions_count'),
    url('^update-words/$', views.update_words, name='update_words'),
    url('^progress/$', views.get_progress, name='get_progress'),
    url('^progress/(?P<pk>\d+)/$', views.get_packet_progress, name='get_packet_progress'),
    url('^add-packets/$', views.add_packets, name='add_packets'),
    url('^clear_all/$', views.clear_all, name='clear_all'),
    url('^mark-words/$', views.mark_words, name='mark_words'),
    url('^unmark-words/$', views.unmark_words, name='unmark_words'),
    url('^get-app/([0-9]*)$', views.get_app, name='get_app'),
    url('^my-words/$', views.ManageWords.as_view(), name='my_words'),
    url('^my-verbs/$', views.ManageVerbs.as_view(), name='my_verbs'),
    url('^my-words-standalone/(?P<lesson_number>[0-9]*)/$', views.manage_words_standalone, name='my_words_standalone'),
    url('^my-words-get-filters/$', views.get_filters, name='get_filters'),
    url('^my-words-save-filters/$', views.save_filters, name='save_filters'),
    url('^app/$', views.start_app, name='app'),
    url('^app/reviews/$', views.start_app_repeat, name='app_repeat'),
    url('^app/verbs/$', views.start_app_verbs, name='app_verbs'),
    url('^verbs/(?P<packet_id>\d+)/$', views.get_verbs, name='get_verbs'),
    url('^verbs/(?P<packet_id>\d+)/(?P<more_lessons>\d+)/$', views.get_verbs, name='get_verbs_more_lessons'),
]

