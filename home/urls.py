from django.conf.urls import url
from . import views

site_import_urls = [
    url(r'^$', views.authorize),
    url(r'^authorized/$', views.authorized)
]

api_urls = [
    url(r'^nav/$', views.get_nav_data)
]