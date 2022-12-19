import json
import os
from email.utils import parseaddr, formataddr

from django import urls
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from donations.forms import SupportForm, CrowdFundingForm
from donations.models import Donation
from home.models import BackUrls
from tinkoff_merchant.consts import DONATIONS
from tinkoff_merchant.models import Payment as TinkoffPayment
from tinkoff_merchant.services import MerchantAPI

from django.conf import settings

class SubmitDonation(View):
	def get(self, request):
		return redirect('donations:donation_page')

	def post(self, request, *args, **kwargs):
		form = SupportForm(request.POST)
		recurrent = request.POST.get('type') == 'recurrent'
		amount = int(request.POST.get('amount'))
		email = request.POST.get('email', None)
		validation_redirect = request.POST.get('validation_redirect', reverse('donations:donation_page'))
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


def get_bank_transfer_currencies() -> dict:
	return json.loads(os.environ.get('BANK_TRANSFER_DATA',
	                                 '{"USD":{"html": "<b>blablabla</b>", "text": "blablabla"}, "EUR":{"html": "<b>blablabla</b>", "text": "blablabla"}}'))

class BankTransfer(TemplateView):
    template_name = 'donations/bank_transfer.html'

    def get_context_data(self, **kwargs):
	    context = super(BankTransfer, self).get_context_data(**kwargs)
	    context['currencies'] = get_bank_transfer_currencies().keys()
	    return context


@login_required
def bank_transfer_get_email(request):
	if request.method == 'POST' and request.user.is_authenticated:
		currency = request.POST.get('currency', None)
		if currency is None:
			return redirect(urls.reverse('donations:bank_transfer')+"?error&bad_request")
		data = get_bank_transfer_currencies()
		messages = (data.get(currency, None))
		if messages is None:
			return redirect(urls.reverse('donations:bank_transfer')+"?error&not_found")
		user = request.user
		if user.get_full_name():
			name = user.get_full_name()
		else:
			name = user.get_username()
		if name.isascii():
			to = formataddr((name, user.email))
		else:
			to = user.email
		subject = f'Details for bank transfer in {currency}'
		message = EmailMultiAlternatives(
			subject=subject,
			body=f"Добрый день!\n\nСпасибо Вам еще раз за готовность нас поддержать! Ниже — реквизиты счета для банковского перевода в {currency}. По любым вопросам не стесняйтесь мне писать на почту, в Телеграм, в личку или на форум.\n\n{messages.get('text')}",
			from_email=settings.DEFAULT_FROM_EMAIL,
			reply_to=[settings.DEFAULT_REPLY_TO_EMAIL],
			to=[to],
		)
		message.attach_alternative(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<p>Добрый день!</p>
<p>Спасибо Вам еще раз за готовность нас поддержать! Ниже — реквизиты счета для банковского перевода в {currency}. По любым вопросам не стесняйтесь мне писать на почту, в Телеграм, в личку или на форум.</p>
{messages.get('html')}
</body>
</html>""", 'text/html')
		message.send()
		return redirect(urls.reverse('donations:bank_transfer')+"?success")
	else:
		return redirect(urls.reverse('donations:bank_transfer'))
