import json

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import defaultfilters
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import Payment
from .services import MerchantAPI
from .signals import payment_update, payment_confirm, payment_refund


@method_decorator(csrf_exempt, name='dispatch')
class Notification(View):
    _merchant_api = None

    @property
    def merchant_api(self):
        if not self._merchant_api:
            self._merchant_api = MerchantAPI()
        return self._merchant_api

    def dispatch(self, request, *args, **kwargs):
        return super(Notification, self).dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        data = json.loads(request.body.decode())

        if data.get('TerminalKey') != self.merchant_api.terminal_key:
            return HttpResponse(b'Bad terminal key', status=400)

        if not self.merchant_api.token_correct(data.get('Token'), data):
            return HttpResponse(b'Bad token', status=400)

        payment = get_object_or_404(Payment, payment_id=data.get('PaymentId'))
        old_status = payment.status

        self.merchant_api.update_payment_from_response(payment, data).save()

        if old_status != 'CONFIRMED' and payment.status == 'CONFIRMED':
            payment_confirm.send(self.__class__, payment=payment)

        if old_status != 'REFUNDED' and payment.status == 'REFUNDED':
            payment_refund.send(self.__class__, payment=payment)

        payment_update.send(self.__class__, payment=payment)

        return HttpResponse(b'OK', status=200)


@user_passes_test(lambda u: u.is_superuser)
def get_log(request:HttpRequest, year, month):
    payments = list(Payment.objects.select_related('receipt').filter(
        Q(status='CONFIRMED') | Q(status='AUTHORIZED'), update_date__year=int(year), update_date__month=int(month)).order_by('update_date'))
    s = ''
    for p in payments:
        for item in p.items():
            s += '{date}\t{amount}\tTinkoff\t{type}\t{closest_activation}\t{email}\n'.format(
                date=defaultfilters.date(p.update_date, "Y-m-d H:i"), amount=p.amount/100, email=p.email(), closest_activation=p.closest_activation,
                type=item.category.split('_')[0]
            )
    return HttpResponse(s, status=200, content_type='text/plain')
