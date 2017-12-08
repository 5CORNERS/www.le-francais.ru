from django.conf.urls import url
from .views import get_page_template

urlpatterns = [
    url('^(?P<page>.+)$', get_page_template)
]