from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^c-t/(?P<uuid>[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})/\?source=(?P<utm_source>.+)/$',
        views.AdCounterRedirectView.as_view(),
        name='creative-click-through'),
    url(r'^c-t/(?P<uuid>[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})/$',
            views.AdCounterRedirectView.as_view(),
            name='creative-click-through_wo_utm'),
    url(r'^test/$', views.TestView.as_view()),
    url(r'^get-html/', views.get_creative, name='get_creative'),
    url(r'^i/(?P<uuid>[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})/$',
        views.image_redirect, name='image_redirect'),
]
