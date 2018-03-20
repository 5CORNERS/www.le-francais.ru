from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<verb>.+)$', views.get_conjugation)
    url(r'^parler$' views.get_parler_table)
]
