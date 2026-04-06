from django.conf.urls import url
from custom_user.api_views import LoginView, RegisterView, SessionRetrievalView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='api-login'),
    url(r'^register/$', RegisterView.as_view(), name='api-register'),
    url(r'^session/(?P<session_id>[a-zA-Z0-9]+)/$', SessionRetrievalView.as_view(), name='api-session'),
]