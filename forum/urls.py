from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^statistics/$', views.statistics_page, name='statistics')
]
