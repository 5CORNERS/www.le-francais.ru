from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('donations/form.html', takes_context=True)
def include_donation_form(context,
                          success_url='/?modal_open=success-donation-modal&payment_success=true',
                          fail_url='/?modal_open=fail-payment-modal&payment_fail=true',
                          validation_redirect=reverse('donations:donation_page')):
	return dict(
		request=context['request'],
		success_url=success_url,
		fail_url=fail_url,
		validation_redirect=validation_redirect
	)

@register.inclusion_tag('donations/head.html')
def donation_head():
	return {}
