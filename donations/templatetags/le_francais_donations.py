from django import template
from django.db.models import Sum
from django.urls import reverse

from donations.forms import SupportForm
from donations.models import Donation, DONATION_TARGET_ADS

register = template.Library()


@register.inclusion_tag('donations/form.html', takes_context=True)
def include_donation_form(context,
                          success_url='/?modal_open=success-donation-modal&payment_success=true',
                          fail_url='/?modal_open=fail-payment-modal&payment_fail=true',
                          validation_redirect=reverse(
                              'donations:donation_page'),
                          support_form=None,
                          default_target=None,
                          show_target=False):
    if support_form is None and context['request'].user.is_authenticated:
        support_form = SupportForm(dict(email=context['request'].user.email))
    elif support_form is None:
        support_form = SupportForm({})
    return dict(
        request=context['request'],
        success_url=success_url,
        fail_url=fail_url,
        validation_redirect=validation_redirect,
        form=support_form,
        show_target=show_target,
        default_target=default_target,
    )


@register.simple_tag()
def acquired(target):
    return Donation.objects.filter(payment__status__in=['CONFIRMED', 'AUTHORIZED'],
          target=int(target)).aggregate(Sum('amount'))['amount__sum'] or 0


@register.inclusion_tag('donations/head.html')
def donation_head():
    return {}
