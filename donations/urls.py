from . import views
from django.conf.urls import url

urlpatterns = [
	url('submit/$', views.SubmitDonation.as_view(), name='donation_action'),
	url('$', views.DonationPage.as_view(), name='donation_page')
]
