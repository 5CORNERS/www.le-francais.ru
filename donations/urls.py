from . import views
from django.conf.urls import url

urlpatterns = [
	url('/submit/$', views.SubmitDonation.as_view(), name='donation_action'),
	url('/crowdfunding/$', views.crowdfunding_page, name='crowdfunding'),
	url('/crowdfunding/form/$', views.crowdfunding_form, name='crowdfunding_form'),
	url('/crowdfunding/submit/$', views.crowdfunding_submit, name='crowdfunding_submit'),
	url('_1/$', views.DonationPage.as_view(), {'template_name': 'base_1.html'}, name='donation_page_1'),
	url('/$', views.DonationPage.as_view(), name='donation_page')
]
