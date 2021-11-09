from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^(?P<line_item>\d+)/(?P<creative>\d+)/(?P<source>.+)/$',
        views.AdCounterRedirectView.as_view(),
        name='ad-counter-redirect'),
    url(r'^test/$', views.TestView.as_view())
]
