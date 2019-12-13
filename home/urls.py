from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^learning-apps/(?P<id>.+)/', views.get_learning_apps_iframe, name='get_learning_apps_iframe')
]

meta_urls = [
    url(r'^manifest.json$', TemplateView.as_view(template_name='meta/manifest.json', content_type='application/json'), name='manifest'),
    url(r'^sw.js', TemplateView.as_view(template_name='meta/sw.js', content_type='application/javascript'), name='sw'),
    url(r'^ffsw.js', TemplateView.as_view(template_name='meta/ffsw.js', content_type='application/javascript'), name='ffsw')
]

site_import_urls = [
    url(r'^$', views.authorize),
    url(r'^authorized/$', views.authorized)
]

service_urls = [
	url(r'^listen/$', views.listen_request),
	url(r'^test_listen/(?P<number>.+?)/$', views.listen_request_test),
	url(r'^check_listen/$', views.listen_request_check),
    url(r'^get_lesson_url/$', views.get_lesson_url, name='get_lesson_url'),
]
api_urls = [
    url(r'^nav/$', views.get_nav_data),
	url(r'^get_lesson_content/(?P<n>.+?)/(?P<render_pdf>.)/(?P<tab_id>.+?)/$', views.get_lesson_content, name='get_lesson_content')
]

payment_urls = [
    url('^success/$', views.PaymentResult.as_view(), name='tinkoff:payment_result_page_success'),
    url('^fail/$', views.PaymentResult.as_view(), name='tinkoff:payment_result_page_fail'),
    url('^wallet_one/$', views.WlletOneNotifications.as_view(), name='wmi_notification'),
    url('^wallet_one_payments/$', views.PaymentsView.as_view(), name='second_payments'),
    url('^$', views.TinkoffPayments.as_view(), name='payments'),
]

modal_urls = [
    url('^download-login-required/$', view=views.modal_download_login_required, name='download_login_required'),
    url('^content-login-required/$', view=views.modal_content_login_required, name='content_login_required'),
    url('^simple-login-required/$', view=views.modal_simple_login, name='simple_login_required'),
]

activate_urls = [
    url('^', views.ActivateLesson.as_view(), name='activate_lesson'),
]

coffee_urls = [
    url('^check/$', views.coffee_amount_check, name='check_amount'),
    url('^get_amount/$', views.get_coffee_amount, name='get_amount'),
    url('^', views.GiveMeACoffee.as_view(), name='give_me_a_coffee'),
]

favicon_urls = [
    url('^browserconfig.xml$', views.redirect2static('favicon/browserconfig.xml'), name='browserconfig.xml'),
    url('^site.webmanifest$', views.redirect2static('favicon/site.webmanifest'), name='site.webmanifest'),
    url('^favicon-16x16.png$', views.redirect2static('favicon/favicon-16x16.png'), name='favicon-16x16.png'),
    url('^favicon-32x32.png$', views.redirect2static('favicon/favicon-32x32.png'), name='favicon-32x32.png'),
    url('^safari-pinned-tab.svg$', views.redirect2static('favicon/safari-pinned-tab.svg'), name='safari-pinned-tab.svg'),
    url('^mstile-70x70.png$', views.redirect2static('favicon/mstile-70x70.png'), name='mstile-70x70.png'),
    url('^apple-touch-icon.png$', views.redirect2static('favicon/apple-touch-icon.png'), name='apple-touch-icon.png'),
    url('^mstile-150x150.png$', views.redirect2static('favicon/mstile-150x150.png'), name='mstile-150x150.png'),
    url('^mstile-310x150.png$', views.redirect2static('favicon/mstile-310x150.png'), name='mstile-310x150.png'),
    url('^favicon-194x194.png$', views.redirect2static('favicon/favicon-194x194.png'), name='favicon-194x194.png'),
    url('^mstile-310x310.png$', views.redirect2static('favicon/mstile-310x310.png'), name='mstile-310x310.png'),
    url('^android-chrome-192x192.png$', views.redirect2static('favicon/android-chrome-192x192.png'), name='android-chrome-192x192.png'),
    url('^favicon.ico$', views.redirect2static('favicon/favicon.ico'), name='favicon.ico'),
    url('^android-chrome-512x512.png$', views.redirect2static('favicon/android-chrome-512x512.png'), name='android-chrome-512x512.png'),
]
