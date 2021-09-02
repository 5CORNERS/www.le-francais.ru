from django import template
from django.db.models import Sum
from django.urls import reverse

from donations.models import Donation, DONATION_TARGET_ADS

register = template.Library()


@register.inclusion_tag('donations/form.html', takes_context=True)
def include_donation_form(context,
                          success_url='/?modal_open=success-donation-modal&payment_success=true',
                          fail_url='/?modal_open=fail-payment-modal&payment_fail=true',
                          validation_redirect=reverse(
                              'donations:donation_page')):
    return dict(
        request=context['request'],
        success_url=success_url,
        fail_url=fail_url,
        validation_redirect=validation_redirect
    )


@register.simple_tag()
def acquired(target):
    return Donation.objects.filter(payment__status__in=['CONFIRMED', 'AUTHORIZED'],
          target=int(target)).aggregate(Sum('amount'))['amount__sum']


@register.inclusion_tag('donations/head.html')
def donation_head():
    return {}
