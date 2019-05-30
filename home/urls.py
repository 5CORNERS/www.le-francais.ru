from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^login/$', views.ajax_login, name='login')
]

meta_urls = [
    url(r'^manifest.json$', TemplateView.as_view(template_name='meta/manifest.json'), name='manifest'),
    url(r'^sw.js', TemplateView.as_view(template_name='meta/sw.js'), name='sw'),
    url(r'^ffsw.js', TemplateView.as_view(template_name='meta/ffsw.js'), name='ffsw')
]

site_import_urls = [
    url(r'^$', views.authorize),
    url(r'^authorized/$', views.authorized)
]

api_urls = [
    url(r'^nav/$', views.get_nav_data),
    url(r'^listen/$', views.listen_request),
    url(r'^get_lesson_url/$', views.get_lesson_url, name='get_lesson_url')
]

payment_urls = [
    url('^success/$', views.PaymentResult.as_view(), name='tinkoff:payment_result_page_success'),
    url('^fail/$', views.PaymentResult.as_view(), name='tinkoff:payment_result_page_fail'),
    url('^wallet_one/$', views.WlletOneNotifications.as_view(), name='wmi_notification'),
    url('^wallet_one_payments/$', views.PaymentsView.as_view(), name='second_payments'),
    url('^$', views.TinkoffPayments.as_view(), name='payments'),
]

modal_urls = [
    url('^download-login-required/$', view=views.modal_login_required, name='login_required')
]

activate_urls = [
    url('^', views.ActivateLesson.as_view(), name='activate_lesson'),
]

coffee_urls = [
    url('^check/$', views.coffee_amount_check, name='check_amount'),
    url('^get_amount/$', views.get_coffee_amount, name='get_amount'),
    url('^', views.GiveMeACoffee.as_view(), name='give_me_a_coffee'),
]
