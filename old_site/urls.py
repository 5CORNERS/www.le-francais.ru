from django.conf.urls import url

from old_site import views

urlpatterns = [
	url('^(?P<page>.+)$', views.get_page_template),
	url('^', views.open_old_site_iframe)
]
