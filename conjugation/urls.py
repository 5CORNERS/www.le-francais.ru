from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'verbs_autocomplete/.{0,50}?/$', views.get_autocomplete_list, name='autocomplete'),
    url(r'search/$', views.search, name='search'),
    url(r"polly/$", views.get_polly_audio_link, name='polly'),
    url(r"(?P<feminin>feminin_)?(?P<se>se_|s_)?(?P<verb>[-'a-zÀ-ÿ]{1,30})(?P<homonym>_2)?/$", views.verb_page, name='verb'),
    url(r'^$', views.index, name='index'),
]
