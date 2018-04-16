from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'verbs_autocomplete/.{0,50}?$', views.get_autocomplete_list),
    url(r'verb/$', views.get_table, name='conjugation'),
    url(r'verb/(?P<verb>.{0,50}?)/', views.get_table, name='conjugation_verb'),
]
