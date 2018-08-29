from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^login/$', views.ajax_login, name='login')
]

site_import_urls = [
    url(r'^$', views.authorize),
    url(r'^authorized/$', views.authorized)
]

api_urls = [
    url(r'^nav/$', views.get_nav_data),
    url(r'^listen/$', views.listen_request),
]

payment_urls = [
    url('^wallet_one/$', csrf_exempt(views.WlletOneNotifications.as_view()), name='wmi_notification'),
    url('^', views.PaymentsView.as_view(), name='payments'),
]
