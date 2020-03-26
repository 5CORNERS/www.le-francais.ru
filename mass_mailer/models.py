import time
import uuid

from annoying.fields import AutoOneToOneField, JSONField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.mail import EmailMessage, send_mass_mail, \
	EmailMultiAlternatives, get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.db import models
from django.forms import SelectMultiple, MultipleChoiceField
from django.template import Context, Template
from django.utils.module_loading import import_string
from django.shortcuts import reverse

User = get_user_model()


class ChoiceArrayField(ArrayField):
	"""
	A field that allows us to store an array of choices.

	Uses Django 1.9's postgres ArrayField
	and a MultipleChoiceField for its formfield.

	Usage:

		choices = ChoiceArrayField(models.CharField(max_length=...,
													choices=(...,)),
								   default=[...])
	"""

	def formfield(self, **kwargs):
		defaults = {
			'form_class': MultipleChoiceField,
			'choices': self.base_field.choices,
		}
		defaults.update(kwargs)
		# Skip our parent's formfield implementation completely as we don't
		# care for it.
		# pylint:disable=bad-super-call
		return super(ArrayField, self).formfield(**defaults)

class Profile(models.Model):
	TAG_DEFAULT = 0
	TAG_CHOICES = [
		(TAG_DEFAULT, 'default'),
	]
	key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
	user = AutoOneToOneField(to=User, related_name='mailer_profile', on_delete=models.CASCADE)
	tags = ChoiceArrayField(default=[], base_field=models.IntegerField(choices=TAG_CHOICES))
	subscribed = models.BooleanField(default=True)

	def get_unsubscribe_url(self):
		domain = 'www.le-francais.ru'
		return 'https://' + domain + reverse("mass_mailer:unsubscribe", kwargs={"key": self.key})


class EmailSettings(models.Model):
	host = models.CharField(max_length=64)
	port = models.CharField(max_length=64)
	username = models.CharField(max_length=64)
	password = models.CharField(max_length=64)
	use_tls = models.BooleanField()
	use_ssl = models.BooleanField()

	messages_per_second = models.IntegerField(default=50)
	messages_per_hour = models.IntegerField(default=300)

	def __str__(self):
		return f'{self.username}@{self.host}:{self.port}'

	def get_backend(self):
		klass = import_string(settings.MASS_EMAIL_BACKEND)
		return klass(host=self.host, port=self.port, username=self.username,
		             password=self.password,
		             use_tls=self.use_tls, fail_silently=False,
		             use_ssl=self.use_ssl,
		             timeout=None,
		             ssl_keyfile=None, ssl_certfile=None)


class UsersFilter(models.Model):
	USERS_WITHOUT_ACTIVATIONS = '0'
	USERS_WITH_PAYMENTS = '1'
	FILTERS = [
		(USERS_WITHOUT_ACTIVATIONS, 'Users w/o activations'),
		(USERS_WITH_PAYMENTS, 'Users with payments'),
	]
	name = models.CharField(max_length=64)
	filters = ChoiceArrayField(
		models.CharField(max_length=12, choices=FILTERS), default=list,
		blank=True
	)
	first_payment_was = models.DateField(null=True)
	last_payment_was = models.DateField(null=True)
	manual_email_list = models.TextField(max_length=1024, help_text='Comma-separated list of emails, for testing purposes.', default=None, null=True)
	ignore_subscriptions = models.BooleanField(default=False)
	send_once = models.BooleanField(default=True)

	def __str__(self):
		return self.name


class Message(models.Model):
	USERS_WITHOUT_ACTIVATIONS = 0
	USERS_WITH_PAYMENTS = 1
	TO_GROUPS_FILTERS = [
		(USERS_WITHOUT_ACTIVATIONS, 'Users w/o activations'),
		(USERS_WITH_PAYMENTS, 'Users with payments'),
	]

	template_subject = models.CharField(max_length=64, blank=True)
	template_html = models.TextField(blank=True, help_text='You can ')
	template_txt = models.TextField(blank=True)
	extra_headers = JSONField(null=True, blank=True, help_text='JSON Format', default=None)
	from_email = models.EmailField(default=settings.DEFAULT_FROM_EMAIL)
	reply_to = models.EmailField(null=True)
	recipients_filter = models.ForeignKey('UsersFilter', null=True, on_delete=models.SET_NULL)
	sent = models.ManyToManyField(to=User, related_name='mass_mailer_received', null=True, blank=True)

	email_settings = models.ForeignKey('EmailSettings', on_delete=models.SET_NULL, null=True)

	created_datetime = models.DateTimeField(auto_now_add=True)
	send_datetime = models.DateTimeField(null=True)

	def __str__(self):
		return f'{self.template_subject}'

	def get_backend(self):
		if self.email_settings:
			return self.email_settings.get_backend()
		else:
			klass = import_string(settings.MASS_EMAIL_BACKEND)
			host     = settings.MASS_EMAIL_HOST
			port     = settings.MASS_EMAIL_PORT
			user     = settings.MASS_EMAIL_HOST_USER
			password = settings.MASS_EMAIL_HOST_PASSWORD
			use_tls  = settings.MASS_EMAIL_USE_TLS
			use_ssl  = settings.MASS_EMAIL_USE_SSL
			return klass(host=host, port=port, username=user, password=password,
	                 use_tls=use_tls, fail_silently=False, use_ssl=use_ssl, timeout=None,
	                 ssl_keyfile=None, ssl_certfile=None)

	def get_recipients(self):
		recipients = User.objects.all()
		if self.recipients_filter:
			if self.recipients_filter.manual_email_list:
				email_list = [email.strip() for email in self.recipients_filter.manual_email_list.split(',')]
				return recipients.filter(email__in=email_list)
			else:
				for recipients_filter in self.recipients_filter.filters.copy():
					if recipients_filter == UsersFilter.USERS_WITH_PAYMENTS:
						from tinkoff_merchant.models import Payment
						payments_query = Payment.objects.filter(status__in=['CONFIRMED', 'AUTHORIZED'])
						if self.recipients_filter.last_payment_was:
							payments_query = payments_query.filter(update_date__lte=self.recipients_filter.last_payment_was)
						if self.recipients_filter.first_payment_was:
							payments_query = payments_query.filter(update_date__gte=self.recipients_filter.first_payment_was)
						wanted_pks = [int(p.customer_key) for p in payments_query]
						recipients = recipients.filter(id__in=wanted_pks)
					elif recipients_filter == UsersFilter.USERS_WITHOUT_ACTIVATIONS:
						recipients = recipients.filter(payment__isnull=True)
			if not self.recipients_filter.ignore_subscriptions:
				recipients = recipients.exclude(pk__in=[p.user.pk for p in
				                                        Profile.objects.filter(
					                                        subscribed=False)])
			if self.recipients_filter.send_once:
				recipients = recipients.exclude(
					pk__in=[u.pk for u in self.sent.all()])
		return recipients

	def send(self):
		backend = self.get_backend()
		emails = []
		recipients = self.get_recipients()
		chunks = [recipients[x:x+self.email_settings.messages_per_second] for x in range(0, len(recipients), self.email_settings.messages_per_second)]
		for chunk in chunks:
			for recipient in chunk:
				header = {
					'List-Unsubscribe': f'<{recipient.mailer_profile.get_unsubscribe_url()}>'
				}
				# header.update(self.extra_headers)
				email_message = EmailMultiAlternatives(
					subject=self.get_subject_for(recipient.mailer_profile),
					from_email=self.from_email,
					to=[recipient.email],
					headers=header,
					reply_to=[self.reply_to],
					body=self.get_txt_body_for(recipient.mailer_profile)
				)
				email_message.attach_alternative(self.get_html_body_for(recipient.mailer_profile), 'text/html')
				emails.append(email_message)
			sent_count = backend.send(emails)
			self.sent.add(*chunk[:sent_count])
			time.sleep(1)

	def get_subject_for(self, recipient):
		return Template(self.template_subject).\
			render(Context(self.get_context(recipient)))

	def get_html_body_for(self, recipient):
		return Template(self.template_html). \
			render(Context(self.get_context(recipient)))

	def get_txt_body_for(self, recipient):
		return Template(self.template_txt).render(
			Context(self.get_context(recipient))
		)

	def get_context(self, recipient):
		from tinkoff_merchant.models import Payment
		last_payment = Payment.objects.filter(customer_key=str(recipient.user.pk), status__in=['CONFIRMED', 'AUTHORIZED']).order_by('update_date').last()
		context = dict(
			user=recipient.user,
			profile=recipient,
			last_payment={
				'date': last_payment.update_date if last_payment else None,
				'cups_count': sum(
					item.site_quantity for item in last_payment.items()) if last_payment else 0
			}
		)
		return context
