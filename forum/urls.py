from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^statistics/$', views.statistics_page, name='statistics'),
    url(r'^post/(?P<pk>\d+)/react/$', views.post_react_ajax, name='react_post'),
    url(r'^post/(?P<pk>\d+)/reactions/$', views.post_reaction_users_ajax, name='post_reactions'),
]

