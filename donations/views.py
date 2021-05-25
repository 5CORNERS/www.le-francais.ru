from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from donations.models import Donation
from home.models import BackUrls
from tinkoff_merchant.consts import DONATIONS
from tinkoff_merchant.models import Payment as TinkoffPayment
from tinkoff_merchant.services import MerchantAPI

@method_decorator(login_required, name='post')
class SubmitDonation(View):
	def get(self, request):
		return redirect('donations:donation_page')

	def post(self, request, *args, **kwargs):
		recurrent = request.POST.get('type') == 'recurrent'
		amount = int(request.POST.get('amount'))
		email = request.user.email
		description = f'Ежемесячное пожертвование le-francais.ru'
		name = f'Одноразовое пожертвование le-francais.ru'
		payment = TinkoffPayment.objects.create(
			amount = amount * 100,
			description=description,
			customer_key=request.user.pk,
			recurrent=recurrent
		).with_receipt(
			email=email,
		).with_items(
			[dict(
				name=name,
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
					'HTTP_HOST'] + request.POST['success_url'],
				fail=request.scheme + "://" + request.META[
					'HTTP_HOST'] +
				     request.POST['fail_url']
			)
			Donation.objects.create(
				amount=amount,
				payment=payment,
				user=request.user,
			)
			return redirect(payment.payment_url)
		else:
			return redirect('donations:donation_page')


@method_decorator(login_required, name='get')
class DonationPage(View):
	def get(self, request):
		return render(request, 'donations/base.html')


# class DonationApiGetInfo(View):
# 	def get(self, request):
# 		return ...
