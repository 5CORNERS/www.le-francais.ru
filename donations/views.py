from email.utils import parseaddr

from django import urls
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from donations.forms import SupportForm, CrowdFundingForm
from donations.models import Donation
from home.models import BackUrls
from tinkoff_merchant.consts import DONATIONS
from tinkoff_merchant.models import Payment as TinkoffPayment
from tinkoff_merchant.services import MerchantAPI


class SubmitDonation(View):
	def get(self, request):
		return redirect('donations:donation_page')

	def post(self, request, *args, **kwargs):
		form = SupportForm(request.POST)
		recurrent = request.POST.get('type') == 'recurrent'
		amount = int(request.POST.get('amount'))
		email = request.POST.get('email', None)
		validation_redirect = request.POST.get('validation_redirect')
		description = 'Ежемесячное пожертвование le-francais.ru' if recurrent else 'Одноразовое пожертвование le-francais.ru'
		comment = request.POST.get('comment')
		target = int(request.POST.get('target', 1))

		if request.user.is_authenticated:
			user = request.user
			user_id = user.pk
			if not email:
				email = user.email
		else:
			user = None
			user_id = None

		payment = TinkoffPayment.objects.create(
			amount = amount * 100,
			description=description,
			customer_key=user_id,
			recurrent=recurrent
		).with_receipt(
			email=email if email else parseaddr(settings.DEFAULT_FROM_EMAIL)[1],
		).with_items(
			[dict(
				name=description,
				price=amount * 100,
				quantity=1,
				amount=amount * 100,
				category=DONATIONS,

			)]
		)
		payment.order_id = '{0:02d}'.format(2) + '{0:06d}'.format(payment.id)

		tinkoff_api = MerchantAPI()
		tinkoff_api.init(payment).save()

		if payment.can_redirect():
			BackUrls.objects.create(
				payment=payment,
				success=request.scheme + "://" + request.META[
					'HTTP_HOST'] + request.POST.get('success_url', '/?modal_open=success-donation-modal&payment_success=true'),
				fail=request.scheme + "://" + request.META[
					'HTTP_HOST'] +
				     request.POST.get('fail_url', '/?modal_open=fail-payment-modal&payment_fail=true')
			)
			Donation.objects.create(
				amount=amount,
				payment=payment,
				user=user,
				comment=comment,
				target=target,
				email=email
			)
			return redirect(payment.payment_url)
		else:
			return redirect(validation_redirect)


class DonationPage(View):
	def get(self, request, template_name='base.html'):
		form = SupportForm({})
		return render(request, f'donations/{template_name}', {'form': form})



def crowdfunding_page(request):
	return render(request, 'donations/crowdfunding.html')


def crowdfunding_form(request):
	return render(request, 'donations/crowdfunding_form.html')


def crowdfunding_submit(request):
	if request.method=='GET':
		return redirect(urls.reverse('donations:crowdfunding_form'))
