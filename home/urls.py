from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

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
    url('^wallet_one/$', views.WlletOneNotifications.as_view(), name='wmi_notification'),
    url('^', views.PaymentsView.as_view(), name='payments'),
]

coffee_urls = [
    url('^check/$', views.coffee_amount_check, name='check_amount'),
    url('^get_amount/$', views.get_coffee_amount, name='get_amount'),
    url('^', views.GiveMeACoffee.as_view(), name='give_me_a_coffee'),
]
