import json
from calendar import monthrange

import tabulate
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseGone
from django.shortcuts import get_object_or_404, render
from django.template import defaultfilters, TemplateDoesNotExist
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from .consts import PAYMENT_STATUS_CONFIRMED, PAYMENT_STATUS_REFUNDED
from .models import Payment, RedirectToPaymentUrl
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

        if old_status != PAYMENT_STATUS_CONFIRMED and payment.status == PAYMENT_STATUS_CONFIRMED:
            payment_confirm.send(self.__class__, payment=payment)

        if old_status != PAYMENT_STATUS_REFUNDED and payment.status == PAYMENT_STATUS_REFUNDED:
            payment_refund.send(self.__class__, payment=payment)

        payment_update.send(self.__class__, payment=payment)

        return HttpResponse(b'OK', status=200)


@user_passes_test(lambda u: u.is_superuser)
def get_log(request:HttpRequest, year, month):
    year = int(year)
    month = int(month)
    payments = list(Payment.objects.select_related('receipt').filter(
        Q(status='CONFIRMED') | Q(status='AUTHORIZED'), update_date__year=year, update_date__month=month).order_by('update_date'))
    header = (
        'DATE','SUM','BANK','TYPE','LESSON','EMAIL', 'username',
        'recurrent',
        'country',
        'city'
    )
    today_income = 0
    total_income = 0
    rows = []
    for p in payments:
        for item in p.items():
            rows.append((
                defaultfilters.date(p.update_date, "Y-m-d H:i"),
                int(p.amount / 100),
                'Tinkoff',
                item.category.split('_')[0],
                p.closest_activation,
                p.email,
                p.username,
                p.recurrent or bool(p.rebill_id),
                p.user.country_name if p.user else 'n/a',
                p.user.city if p.user else 'n/a'
            ))
        total_income += int(p.amount/100)
        if p.update_date.day == timezone.now().day:
            today_income += int(p.amount/100)
    # s = tabulate.tabulate(s, headers='firstrow')
    # s += f'\n----------------------------\n'
    # s += f'Today Income: {today_income}\n'
    # s += f'Total Income: {total_income}\n'
    # s += f'Average Daily: {total_income/timezone.now().day}'
    if timezone.now().month == month and timezone.now().year == year:
        average_daily_income = total_income / timezone.now().day
    else:
        average_daily_income = total_income / monthrange(year, month)[1]
    return render(request, 'tinkoff/log.html', {
        'header': header, 'rows': rows, 'today': today_income,
        'total': total_income,
        'average_daily': average_daily_income,
        'year': year, 'month': month
    })


def redirect_to_payment(request, uuid):
    redirect2payment = RedirectToPaymentUrl.objects.get(uuid=uuid)
    if redirect2payment.payment.can_redirect():
        redirect2payment.visited = timezone.now()
        redirect2payment.save()
        return HttpResponseRedirect(redirect2payment.payment.payment_url)
    else:
        try:
            return render(request, '410.html', status=410)
        except TemplateDoesNotExist:
            return HttpResponseGone()
