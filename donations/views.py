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


class SubmitDonation(View):
	def get(self, request):
		return redirect('donations:donation_page')

	def post(self, request, *args, **kwargs):
		recurrent = request.POST.get('type') == 'recurrent'
		amount = int(request.POST.get('amount'))
		email = request.POST.get('email', None)
		validation_redirect = request.POST.get('validation_redirect')
		description = 'Ежемесячное пожертвование le-francais.ru' if recurrent else 'Одноразовое пожертвование le-francais.ru'
		comment = request.POST.get('comment')
		target = int(request.POST.get('target'))

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
			email=email,
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
					'HTTP_HOST'] + request.POST['success_url'],
				fail=request.scheme + "://" + request.META[
					'HTTP_HOST'] +
				     request.POST['fail_url']
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
	def get(self, request):
		return render(request, 'donations/base.html')


# class DonationApiGetInfo(View):
# 	def get(self, request):
# 		return ...
