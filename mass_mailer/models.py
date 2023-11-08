import smtplib
from datetime import datetime, timedelta
from email.utils import formataddr

from django.db.models import Q, Count, Sum, Case, When, F, \
	DecimalField, IntegerField, Max
from django.db.models.functions import Cast
from django.utils import timezone
from typing import Tuple

import time
import uuid

from annoying.fields import AutoOneToOneField, JSONField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField, DateRangeField
from django.core.mail import EmailMessage, send_mass_mail, \
	EmailMultiAlternatives, get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.db import models
from django.forms import SelectMultiple, MultipleChoiceField
from django.template import Context, Template
from django.utils.module_loading import import_string
from django.shortcuts import reverse
from postman.api import pm_broadcast
from user_sessions.models import Session
from validate_email import validate_email

from tinkoff_merchant.consts import PAYMENT_STATUS_CHOICES, \
	CATEGORIES as PAYMENT_ITEM_CATEGORY, CATEGORIES
from tinkoff_merchant.models import Payment

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

PROFILE_STATUS_OK = 'ok'
PROFILE_STATUS_EMAIL_NOT_EXIST = 'not_exist'
PROFILE_STATUS_CHOICES = [
	(PROFILE_STATUS_OK, 'OK'),
	(PROFILE_STATUS_EMAIL_NOT_EXIST, 'Email not exist')
]
class Profile(models.Model):
	TAG_DEFAULT = 0
	TAG_CHOICES = [
		(TAG_DEFAULT, 'default'),
	]
	key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
	user = AutoOneToOneField(to=User, related_name='mailer_profile', on_delete=models.CASCADE, null=True, blank=True)
	subscribed = models.BooleanField(default=True)
	_email = models.EmailField(blank=True, null=True)
	status = models.CharField(choices=PROFILE_STATUS_CHOICES, default=PROFILE_STATUS_OK, max_length=16)
	comment = models.CharField(max_length=1024, blank=True, null=True)

	def get_unsubscribe_url(self):
		domain = 'www.le-francais.ru'
		return 'https://' + domain + reverse("mass_mailer:unsubscribe", kwargs={"key": self.key})

	@property
	def email(self):
		if self.user:
			return self.user.email
		else:
			return self._email

	def __str__(self):
		if self.user:
			return f"{self.user.username} <{self.email}>"
		else:
			return self.email


class EmailSettings(models.Model):
	host = models.CharField(max_length=64)
	port = models.CharField(max_length=64)
	username = models.CharField(max_length=64)
	password = models.CharField(max_length=64)
	use_tls = models.BooleanField()
	use_ssl = models.BooleanField()

	sender_email = models.EmailField(null=True)
	sender_username = models.CharField(max_length=100, null=True)

	messages_per_connection = models.IntegerField(default=35)
	delay_between_connections = models.IntegerField(default=10, help_text='In seconds')

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

	def get_sender_header(self):
		return f'{self.sender_username} <{self.sender_email}>'
#
#
# class BlackList(models.Model):
# 	name = models.CharField(max_length=64)
# 	users = models.ManyToManyField(User)
#
# 	def __str__(self):
# 		return f"{self.name}"


class UsersFilter(models.Model):
	USERS_WITH_PAYMENTS_LTE10 = '10'
	USERS_WITHOUT_ACTIVATIONS = '0'
	USERS_WITH_PAYMENTS = '1'
	PAYMENTS_WITHOUT_ACTIVATIONS = '2'
	USERS_WITH_PAYMENTS_EQ1CUP = '3'
	USERS_WITH_PAYMENTS_GT1CUP = '4'
	USERS_WITH_PAYMENTS_EQ5CUP = '5'
	USERS_WITH_PAYMENTS_EQ10CUP = '6'
	USERS_WITH_PAYMENTS_EQ20CUP = '7'
	USERS_WITH_PAYMENTS_EQ50CUP = '8'
	USERS_WITHOUT_PAYMENTS = '9'
	FILTERS = [
		(USERS_WITHOUT_ACTIVATIONS, 'Users w/o activations'),
		(USERS_WITH_PAYMENTS, 'Users with payments'),
		(PAYMENTS_WITHOUT_ACTIVATIONS, 'Payments w/o activations'),
		(USERS_WITH_PAYMENTS_EQ1CUP, 'Users, which payed for 1 cup only'),
		(USERS_WITH_PAYMENTS_GT1CUP, 'Users, which payed for more than 1 cups'),
		(USERS_WITH_PAYMENTS_EQ5CUP, 'Users, which payed for 5 cups only'),
		(USERS_WITH_PAYMENTS_EQ10CUP, 'Users, which payed for 10 cups only'),
		(USERS_WITH_PAYMENTS_EQ20CUP, 'Users, which payed for 20 cups only'),
		(USERS_WITH_PAYMENTS_EQ50CUP, 'Users, which payed for 50 cups only'),
		(USERS_WITHOUT_PAYMENTS, 'Users w/o payments'),
		(USERS_WITH_PAYMENTS_LTE10, 'Users with payments for 10 or less cups or tickets including 0')
	]
	name = models.CharField(max_length=64)
	filters = ChoiceArrayField(
		models.CharField(max_length=12, choices=FILTERS), default=list,
		blank=True
	)
	first_payment_was = models.DateField(null=True, blank=True)
	last_payment_was = models.DateField(null=True, blank=True)

	joined_before = models.DateField(null=True, blank=True)
	joined_after = models.DateField(null=True, blank=True)

	last_activity_before = models.DateField(null=True, blank=True, help_text="Sessions Only")
	last_activity_after = models.DateField(null=True, blank=True)

	min_lesson_number = models.IntegerField(null=True, blank=True)
	logged_more_than_once = models.BooleanField(default=True, blank=True)

	has_name_for_emails = models.BooleanField(default=False)

	blacklist = models.ManyToManyField(to=User, blank=True)
	manual_email_list = models.TextField(help_text='Comma-separated list of emails, for testing purposes.', default=None, null=True, blank=True)
	manual_blacklist = models.TextField(blank=True, null=True, default=None)
	ignore_subscriptions = models.BooleanField(default=False)
	send_once = models.BooleanField(default=True)
	send_once_in_days = models.IntegerField(blank=True, null=True)
	send_to_not_validated = models.BooleanField(default=True)

	send_only_first = models.IntegerField(null=True, blank=True, default=None)
	do_not_send_to_pass_partout = models.BooleanField(default=False)

	do_not_send_to_gmail = models.BooleanField(default=False)
	do_not_send_to_yandex = models.BooleanField(default=False)
	do_not_send_to_mailru = models.BooleanField(default=False)
	do_not_send_to_comcast = models.BooleanField(default=False)

	send_only_to_gmail = models.BooleanField(default=False)

	cups_amount_gte = models.IntegerField(null=True, blank=True, default=None)

	payments_statuses = ChoiceArrayField(models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES), blank=True, null=True)
	payments_range = DateRangeField(null=True, blank=True, help_text='Bounds works as [,)')
	payments_range_days = IntegerField(null=True, blank=True)
	payments_exclude = models.BooleanField(default=False)
	payments_category = ChoiceArrayField(models.CharField(max_length=20, choices=CATEGORIES), blank=True, null=True)

	payments_statuses_b = ChoiceArrayField(models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES), blank=True, null=True)
	payments_range_b = DateRangeField(null=True, blank=True, help_text='Bounds works as [,)')
	payments_range_days_b = IntegerField(null=True, blank=True)
	payments_exclude_b = models.BooleanField(default=False)
	payments_category_b = ChoiceArrayField(models.CharField(max_length=20, choices=CATEGORIES), blank=True, null=True)

	payments_statuses_c = ChoiceArrayField(models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES), blank=True, null=True)
	payments_range_c = DateRangeField(null=True, blank=True, help_text='Bounds works as [,)')
	payments_range_days_c = IntegerField(null=True, blank=True)
	payments_exclude_c = models.BooleanField(default=False)
	payments_category_c = ChoiceArrayField(models.CharField(max_length=20, choices=CATEGORIES), blank=True, null=True)

	recipient_country = ChoiceArrayField(models.CharField(max_length=2,choices=[
		('RU', 'Russia'),
		('FR', 'France'),
		('UA', 'Ukraine'),
		('BY', 'Belarus'),
		('KZ', 'Kazakhstan'),
		('DE', 'Germany'),
		('BE', 'Belgium'),
		('CH', 'Switzerland'),
		('CA', 'Canada'),
		('NL', 'Netherlands'),
		('PL', 'Poland'),
		('US', 'United States'),
		('GB', 'United Kingdom'),
		('ES', 'Spain'),
		('IT', 'Italy'),
		('UZ', 'Uzbekistan'),
		('CZ', 'Czechia'),
		('LV', 'Latvia'),
		('AM', 'Armenia'),
		('TR', 'Turkey'),
		('MD', 'Moldova'),
		('EE', 'Estonia'),
		('IL', 'Israel'),
		('LU', 'Luxembourg'),
		('GE', 'Georgia'),
		('LT', 'Lithuania'),
		('KG', 'Kyrgyzstan'),
		('AE', 'United Arab Emirates'),
		('AZ', 'Azerbaijan'),
		('FI', 'Finland'),
		('BG', 'Bulgaria'),
		('ME', 'Montenegro'),
		('SE', 'Sweden'),
		('IE', 'Ireland'),
		('RS', 'Serbia'),
		('RO', 'Romania'),
		('TH', 'Thailand'),
		('KR', 'South Korea'),
		('AT', 'Austria'),
		('IN', 'India'),
		('TJ', 'Tajikistan'),
		('BR', 'Brazil'),
		('CY', 'Cyprus'),
		('NO', 'Norway'),
		('VN', 'Vietnam'),
		('GN', 'Guinea'),
		('DK', 'Denmark'),
		('SK', 'Slovakia'),
		('MA', 'Morocco'),
		('CI', 'Ivory Coast'),
		('NC', 'New Caledonia'),
		('BJ', 'Benin'),
		('TN', 'Tunisia'),
		('CL', 'Chile'),
		('AG', 'Antigua and Barbuda'),
		('ID', 'Indonesia'),
		('DZ', 'Algeria'),
		('SG', 'Singapore'),
		('LK', 'Sri Lanka'),
		('ZA', 'South Africa'),
		('PT', 'Portugal'),
		('SC', 'Seychelles'),
		('MC', 'Monaco'),
		('HK', 'Hong Kong'),
		('LA', 'Laos'),
		('BH', 'Bahrain'),
		('CD', 'DR Congo'),
		('GR', 'Greece'),
		('NG', 'Nigeria'),
		('MN', 'Mongolia'),
		('MY', 'Malaysia'),
		('MX', 'Mexico'),
		('MV', 'Maldives'),
		('MU', 'Mauritius'),
		('AU', 'Australia'),
		('LB', 'Lebanon')]), blank=True, null=True)

	def __str__(self):
		return self.name

	def get_recipients(self):
		recipients = User.objects.filter(is_active=True)
		if self:
			if self.manual_email_list:
				email_list = [email.strip() for email in
				              self.manual_email_list.split(',')]
				return recipients.filter(email__in=email_list)
			else:
				for recipients_filter in self.filters.copy():
					if recipients_filter == UsersFilter.USERS_WITH_PAYMENTS:
						payments_query = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							amount__gte=10000)
						payments_query = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments_query)
						wanted_pks = [int(p.customer_key) for p in
						              payments_query if p.customer_key if p.customer_key]
						recipients = recipients.filter(id__in=wanted_pks)

					elif recipients_filter == UsersFilter.USERS_WITHOUT_ACTIVATIONS:
						recipients = recipients.filter(payment__isnull=True)

					elif recipients_filter == UsersFilter.PAYMENTS_WITHOUT_ACTIVATIONS:

						payments_query = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'])

						payments_query = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments_query)

						payments = [p for p in list(payments_query) if
						            p.closest_activation == '-']
						recipients = recipients.filter(
							id__in=[int(p.customer_key) for p in payments if p.customer_key])

					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_EQ1CUP:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity = 1,
							receipt__receiptitem__category='coffee_cups'

						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(
							id__in=[int(p.customer_key) for p in payments if p.customer_key]
						)

					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_GT1CUP:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity__gt=1,
							receipt__receiptitem__category='coffee_cups'
						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(
							id__in=[int(p.customer_key) for p in payments if p.customer_key]
						)
					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_EQ5CUP:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity=5
						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(id__in=[int(p.customer_key) for p in payments if p.customer_key])
					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_EQ10CUP:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity=10
						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(id__in=[int(p.customer_key) for p in payments if p.customer_key])
					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_EQ20CUP:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity=20
						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(id__in=[int(p.customer_key) for p in payments if p.customer_key])
					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_EQ50CUP:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity=50
						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(id__in=[int(p.customer_key) for p in payments if p.customer_key])
					elif recipients_filter == UsersFilter.USERS_WITHOUT_PAYMENTS:
						payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
						)
						payments = self.first_last_payments_filter(
							self.first_payment_was, self.last_payment_was,
							payments)
						recipients = recipients.filter(~Q(id__in=[int(p.customer_key) for p in payments if p.customer_key]))
					elif recipients_filter == UsersFilter.USERS_WITH_PAYMENTS_LTE10:
						all_payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
						)
						less_then_equal_10_payments = Payment.objects.filter(
							status__in=['CONFIRMED', 'AUTHORIZED'],
							receipt__receiptitem__site_quantity__lte=10
						)
						all_payments = self.first_last_payments_filter(
							self.first_payment_was,
							self.last_payment_was,
							all_payments)
						less_then_equal_10_payments = self.first_last_payments_filter(
							self.first_payment_was,
							self.last_payment_was,
							less_then_equal_10_payments)
						recipients = recipients.filter(~Q(
							id__in=[int(p.customer_key) for p in
							all_payments if p.customer_key]) | Q(
							id__in=[int(p.customer_key) for p in
							less_then_equal_10_payments if p.customer_key]))

			if self.blacklist.exists():
				recipients = recipients.exclude(
					pk__in=self.blacklist.all()
				)
			if self.joined_before:
				recipients = recipients.filter(
					date_joined__lte=self.joined_before
				)
			if self.joined_after:
				recipients = recipients.filter(
					date_joined__gte=self.joined_after
				)
			if self.cups_amount_gte:
				recipients = recipients.filter(
					_cup_amount__gte=self.cups_amount_gte
				)
			if self.min_lesson_number:
				recipients = recipients.filter(log_messages__message__regex=r"^\d+$").distinct().annotate(
					max_lesson_logged=Max(Case(
						When(Q(log_messages__type=2)|Q(log_messages__type=1, log_messages__value__gte=60), then=Cast('log_messages__message', models.IntegerField())),
						default=0, output_field=models.IntegerField()
					))).filter(max_lesson_logged__gte=self.min_lesson_number)
			if self.last_activity_before:
				user_pks = Session.objects.filter(
					last_activity__lte=self.last_activity_before,
					user__isnull=False
				).values_list('user_id', flat=True).distinct()
				recipients.filter(pk__in=user_pks)
			if self.last_activity_after:
				user_pks = Session.objects.filter(
					last_activity__gte=self.last_activity_after,
					user__isnull=False
				).values_list('user_id', flat=True).distinct()
				recipients.filter(pk__in=user_pks)
			if self.manual_blacklist:
				blacklist = self.manual_blacklist.split(",")
				recipients = recipients.exclude(email__in=blacklist)
			if self.has_name_for_emails:
				recipients = recipients.exclude(name_for_emails__isnull=True)
			if self.do_not_send_to_pass_partout:
				recipients = recipients.exclude(must_pay=False)
			if self.do_not_send_to_gmail:
				recipients = recipients.exclude(email__contains='@gmail.com')
			if self.do_not_send_to_mailru:
				recipients = recipients.exclude(email__contains='@mail.ru')
			if self.do_not_send_to_yandex:
				recipients = recipients.exclude(email__contains='@yandex.ru').exclude(email__contains='@ya.ru')
			if self.do_not_send_to_comcast:
				recipients = recipients.exclude( email__contains='@comcast.net')
			if self.send_only_to_gmail:
				recipients = recipients.filter(email__contains='@gmail.com')
			if True:
				recipients = recipients.annotate(
					payments_amount_sum=Sum(Case(When(
						tinkoff_payment__status__in=['CONFIRMED',
						                             'AUTHORISED'],
						then=F('tinkoff_payment__amount')),
						output_field=IntegerField(),
						default=0))
				).order_by('payments_amount_sum')
			if self.logged_more_than_once:
				recipients = recipients.annotate(
					last_login_date=Cast('last_login', models.DateField())
				).exclude(Q(date_joined__date=F('last_login_date'))|Q(last_login__isnull=True))
			recipients = self.filter_by_payments(recipients)
			if self.recipient_country:
				recipients = recipients.filter(country_code__in=self.recipient_country)
		return recipients

	def iter_payments_filters(self):
		return iter([
			(self.payments_statuses, self.payments_range, self.payments_range_days, self.payments_exclude, self.payments_category),
			(self.payments_statuses_b, self.payments_range_b, self.payments_range_days_b, self.payments_exclude_b, self.payments_category_b),
			(self.payments_statuses_c, self.payments_range_c, self.payments_range_days_c, self.payments_exclude_c, self.payments_category_c)
		])

	def filter_user_payments(self, user:User):
		user_payments = Payment.objects.filter(customer_key=str(user.pk)).order_by('creation_date')
		for p_statuses, p_range, p_range_days, p_exclude, p_categories in self.iter_payments_filters():
			iteration = Payment.objects.filter(customer_key=str(user.pk))
			if p_statuses or p_range is not None or p_range_days is not None or p_categories:
				if p_statuses:
					iteration = iteration.filter(status__in=p_statuses)
				if p_range is not None:
					iteration = iteration.filter(creation_date__date__range=p_range)
				if p_range_days is not None:
					iteration = iteration.filter(creation_date__gte=timezone.now().date() - timedelta(days=p_range_days))
				if p_categories:
					iteration = iteration.filter(receipt__receiptitem__category__in=p_categories)
				if iteration.count():
					pks = iteration.values_list('pk', flat=True)
					if p_exclude:
						user_payments.exclude(pk__in=pks)
					else:
						user_payments.filter(pk__in=pks)
		return user_payments
	def filter_by_payments(self, query):
		for p_statuses, p_range, p_range_days, p_exclude, p_categories in self.iter_payments_filters():
			payments = Payment.objects.all()
			if p_statuses or p_range is not None or p_range_days is not None or p_categories:
				if p_statuses:
					payments = payments.filter(status__in=p_statuses)
				if p_range is not None:
					payments = payments.filter(creation_date__date__range=p_range)
				if p_range_days is not None:
					payments = payments.filter(creation_date__gt=timezone.now() - timedelta(days=p_range_days))
				if p_categories:
					payments = payments.filter(receipt__receiptitem__category__in=p_categories)
				if payments.count():
					user_pks = payments.filter(customer_key__isnull=False).annotate(customer_id=Cast('customer_key', models.IntegerField())).values_list('customer_id', flat=True).distinct()
					if p_exclude:
						query = query.exclude(pk__in=user_pks)
					else:
						query = query.filter(pk__in=user_pks)
				else:
					if p_exclude:
						pass
					else:
						return query.none()
		return query

	@staticmethod
	def first_last_payments_filter(first_payment_date, last_payment_date,
	                               payments_query):
		# FIXME filter users which have payments outside range
		if last_payment_date:
			payments_query = payments_query.filter(
				update_date__lte=timezone.make_aware(
					datetime.combine(last_payment_date, datetime.min.time())))
		if first_payment_date:
			payments_query = payments_query.filter(
				update_date__gte=timezone.make_aware(
					datetime.combine(first_payment_date, datetime.min.time())))
		return payments_query

	@staticmethod
	def filter_users_by_payments(users, payments):
		users.exclude()

	def get_recipients_for_message(self, message):
		"""
		:type message: Message
		"""
		recipients = self.get_recipients()
		if self.send_once:
			recipients = recipients.exclude(
				pk__in=[log.recipient_id for log in MessageLog.objects.filter(result__in=MessageLog.RESULTS_SUCCESS, message=message)])
		elif self.send_once_in_days:
			recipients = recipients.exclude(
				pk__in=MessageLog.objects.filter(
					result__in=MessageLog.RESULTS_SUCCESS,
					message=message,
					sent_datetime__date__gte=(timezone.now() - timedelta(days=self.send_once_in_days)).date()
				).values_list('recipient_id', flat=True)
			)
		if not self.send_to_not_validated:
			recipients = recipients.exclude(
				pk__in=MessageLog.objects.filter(result__in=MessageLog.RESULTS_FAILURE,
					message=message).distinct().values_list('recipient_id', flat=True)
			)
		return recipients


class Message(models.Model):
	name = models.CharField(max_length=64, blank=True, null=True, unique=True)

	template_subject = models.CharField(max_length=1000, blank=True)
	template_html = models.TextField(blank=True, help_text='You can ')
	template_txt = models.TextField(blank=True)

	from_username = models.CharField(max_length=64)
	from_email = models.EmailField()

	reply_to_username = models.CharField(max_length=64, null=True, blank=True)
	reply_to_email = models.EmailField(null=True, blank=True)

	extra_headers = JSONField(help_text='JSON Dict Format', default=dict, blank=True)

	email_settings = models.ForeignKey('EmailSettings', on_delete=models.SET_NULL, null=True, blank=True)
	recipients_filter = models.ForeignKey('UsersFilter', null=True, blank=True, on_delete=models.SET_NULL)

	sent = models.ManyToManyField(to=User, related_name='mass_mailer_received', null=True, blank=True)
	was_sent_to = models.ManyToManyField(
		User,
		through='mass_mailer.MessageLog',
		through_fields=('message', 'recipient'),
		related_query_name='received_mass_mailer_messages'
	)

	created_datetime = models.DateTimeField(auto_now_add=True, blank=True)
	send_datetime = models.DateTimeField(null=True, blank=True)

	list_unsubscribe_header = models.BooleanField(default=False)

	postman_broadcast = models.BooleanField(default=False, help_text="Private messages for users, who, for some reason, can't or won't receive emails")
	postman_subject = models.CharField(max_length=120, blank=True)
	postman_body = models.TextField(blank=True)
	postman_sender = models.ForeignKey(
		User, related_name="postmaster_broadcast_messages",
		null=True, blank=True, )

	validate_emails = models.BooleanField(default=True)

	bcc = ArrayField(models.EmailField(), default=list, blank=True)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._recipients = None
		self._contexts = {}

	def __str__(self):
		return f'{self.name} — {self.template_subject}'

	def get_reply_to_header(self):
		if self.reply_to_email:
			return [f'{self.reply_to_username} <{self.reply_to_email}>']
		return None

	def get_backend(self):
		if self.email_settings:
			return self.email_settings.get_backend()
		else:
			klass = import_string(settings.MASS_EMAIL_BACKEND)
			if settings.MASS_EMAIL_BACKEND.endswith('smtp.EmailBackend'):
				host     = settings.MASS_EMAIL_HOST
				port     = settings.MASS_EMAIL_PORT
				user     = settings.MASS_EMAIL_HOST_USER
				password = settings.MASS_EMAIL_HOST_PASSWORD
				use_tls  = settings.MASS_EMAIL_USE_TLS
				use_ssl  = settings.MASS_EMAIL_USE_SSL
				return klass(host=host, port=port, username=user, password=password,
		                 use_tls=use_tls, fail_silently=False, use_ssl=use_ssl, timeout=None,
		                 ssl_keyfile=None, ssl_certfile=None)
			else:
				return klass()

	def set_recipients(self):
		self._recipients = self.recipients_filter.get_recipients_for_message(message=self)

	def get_recipients(self):
		if self._recipients is None:
			if self.recipients_filter:
				self._recipients = self.recipients_filter.get_recipients_for_message(
					message=self)
		return self._recipients.exclude(pk__in=[p.user.pk for p in  Profile.objects.filter(
			subscribed=False, user__isnull=False)])

	def get_recipients_without_filtering_profiles(self):
		if self._recipients is None:
			self.set_recipients()
		return self._recipients

	def send_manual(self, data_list:list):
		# data_list syntax:
		# [
		# 	{
		# 	'email': <email>,
		# 	'name': <name>,
		# 	'context':
		# 		{
		#			'subject': <subject>,
		#			'domain': 'www.le-francais.ru',
		#			'...': <...>,
		# 		}
		# },...]
		backend: EmailBackend = self.get_backend()
		sent_count = 0
		errors_count = 0
		chunks = [data_list[x:x + self.email_settings.messages_per_connection] for x in range(0, len(data_list), self.email_settings.messages_per_connection)]
		for chunk in chunks:
			to_send = []
			for data in chunk:
				to = data['email']
				context = data['context']
				is_validated = validate_email(
					email_address=to,
					check_regex=True,
					check_mx=True,
					smtp_timeout=10,
					dns_timeout=10,
					use_blacklist=True)
				if not is_validated and is_validated is not None:
					MessageLog.objects.create(
						message=self,
						result=MessageLog.RESULT_FAILURE,
						log_message=str(f"Can't Validate EMail: {to}")
					)
					continue

				header = {
					'Sender': f'{self.email_settings.get_sender_header()}',
				}
				if self.extra_headers:
					for name, value in self.extra_headers.items():
						header[name] = value
				if self.from_username.isascii():
					from_email = formataddr((self.from_username, self.from_email))
				else:
					from_email = self.from_email
				if data["name"].isascii():
					to = formataddr((data["name"], data["email"]))
				else:
					to = data["email"]
				email_message = EmailMultiAlternatives(
					subject=Template(self.template_subject).render(Context(data['context'])),
					from_email=from_email,
					to=[to],
					headers=header,
					reply_to=self.get_reply_to_header(),
					body=Template(self.template_txt).render(Context(data['context'])),
					bcc=list(self.bcc) if self.bcc else None
				)
				if self.template_html:
					email_message.attach_alternative(Template(self.template_html).render(Context(data["context"])), 'text/html')

				to_send.append(email_message)
			backend.open()
			for message in to_send:
				try:
					backend.send_messages([message])
					sent_count += 1
					MessageLog.objects.create(
						result=MessageLog.RESULT_SUCCESS,
						message=self,
						log_message=f'Message to {message.to} was sent'
					)
					time.sleep(1)
				except (smtplib.SMTPSenderRefused,
				        smtplib.SMTPRecipientsRefused,
				        smtplib.SMTPDataError,
				        smtplib.SMTPAuthenticationError) as error:
					MessageLog.objects.create(
						result=MessageLog.RESULT_FAILURE,
						message=self,
						log_message=f'Message to {message.to} wasn\'t sent\n{error}'
					)
					errors_count += 1
					print(f"SMTP Error: {str(error)}")
			backend.close()
			time.sleep(self.email_settings.delay_between_connections)
		return sent_count, errors_count


	def send(self, to=None, users_context=None) -> Tuple[int, int]:
		"""
		:param to: list of users
		:param users_context: dict with users ids as keys and values as context
		:return: count of success, count of failures
		"""
		backend:EmailBackend = self.get_backend()
		if not to:
			recipients = self.get_recipients_without_filtering_profiles()
		else:
			recipients = to

		subscribed_recipients = recipients.exclude(pk__in=[p.user_id for p in
		                                                   Profile.objects.filter(
			                                                   subscribed=False, user__isnull=False)])
		unsubscribed_recipients = recipients.filter(pk__in=[p.user.pk for p in
		                                                    Profile.objects.filter(
			                                                    subscribed=False, user__isnull=False)])
		sent_count = 0
		errors_count = 0
		postman_recipients = list(unsubscribed_recipients)
		if not subscribed_recipients:
			if postman_recipients and self.postman_broadcast:
				self.sent_postman(postman_recipients)
			return sent_count, errors_count
		if self.recipients_filter and self.recipients_filter.send_only_first:
			subscribed_recipients = subscribed_recipients[:self.recipients_filter.send_only_first]
		if self.email_settings:
			chunk_size = self.email_settings.messages_per_connection
			delay = self.email_settings.delay_between_connections
			sender_header = self.email_settings.get_sender_header()
		else:
			chunk_size = settings.MASS_MAILER_DEFAULT_CHUNK_SIZE
			delay = settings.MASS_MAILER_DEFAULT_DELAY
			sender_header = settings.DEFAULT_FROM_EMAIL
		chunks = [subscribed_recipients[x:x+chunk_size] for x in range(0, len(subscribed_recipients), chunk_size)]
		for i, chunk in enumerate(chunks):
			messages_with_recipients = []
			for recipient in chunk:
				if self.validate_emails:
					is_validated = validate_email(
						email_address=recipient.email,
						check_regex=True,
						check_mx=True,
						smtp_timeout=10,
						dns_timeout=10,
						use_blacklist=True)
					if not is_validated and is_validated is not None:
						MessageLog.objects.log(self, recipient, MessageLog.RESULT_FAILURE,
											   log_message=str(f"Can't Validate EMail"))
						errors_count += 1
						postman_recipients.append(recipient)
						continue
				header = {
					'Sender': sender_header,
				}
				if self.list_unsubscribe_header:
					header['List-Unsubscribe'] = f'<{recipient.mailer_profile.get_unsubscribe_url()}>'
				if self.extra_headers:
					for name, value in self.extra_headers.items():
						header[name] = value
				if users_context and recipient.pk in users_context.keys():
					additional_context = users_context[recipient.pk]
				else:
					additional_context = None
				if self.from_username.isascii():
					from_email = formataddr((self.from_username, self.from_email))
				else:
					from_email = self.from_email
				if recipient.username.isascii():
					to = formataddr((recipient.username, recipient.email))
				else:
					to = recipient.email
				email_message = EmailMultiAlternatives(
					subject=self.get_subject_for(recipient.mailer_profile, additional_context),
					from_email=from_email,
					to=[to],
					headers=header,
					reply_to=self.get_reply_to_header(),
					body=self.get_txt_body_for(recipient.mailer_profile, additional_context)
				)
				if self.template_html:
					email_message.attach_alternative(self.get_html_body_for(recipient.mailer_profile, additional_context), 'text/html')
				messages_with_recipients.append((email_message, recipient))

			backend.open()
			for message, recipient in messages_with_recipients:
				try:
					backend.send_messages([message])
					sent_count += 1
					MessageLog.objects.log(self, recipient, MessageLog.RESULT_SUCCESS, f'Message was sent to {recipient.email}')
				except (smtplib.SMTPSenderRefused,
				        smtplib.SMTPRecipientsRefused,
				        smtplib.SMTPDataError,
				        smtplib.SMTPAuthenticationError) as error:
					MessageLog.objects.log(self, recipient, MessageLog.RESULT_FAILURE,
					                       log_message=str(error))
					errors_count += 1
					print(f"SMTP Error: {str(error)}")
			backend.close()
			if i != len(chunks) -1:
				time.sleep(delay)

		if postman_recipients and self.postman_broadcast:
			self.sent_postman(postman_recipients)
		return sent_count, errors_count

	def sent_postman(self, recipients):
		for recipient in recipients:
			pm_broadcast(sender=self.postman_sender,
			             recipients=recipient,
			             subject=self.get_postman_subject_for(recipient),
			             body=self.get_postman_body_for(recipient),
			             skip_notification=True
			             )
			MessageLog.objects.log(self, recipient,
			                       MessageLog.RESULT_POSTMAN_SUCCESS,
			                       f'Message was sent to {recipient.email} by postman')

	def get_subject_for(self, recipient, additional_context=None):
		return Template(self.template_subject).\
			render(Context(self.get_context(recipient, additional_context, include_subject=False)))

	def get_html_body_for(self, recipient, additional_context=None):
		return Template(self.template_html). \
			render(Context(self.get_context(recipient, additional_context)))

	def get_txt_body_for(self, recipient, additional_context=None):
		return Template(self.template_txt).render(
			Context(self.get_context(recipient, additional_context))
		)

	def get_postman_subject_for(self, recipient, additional_context=None):
		return Template(self.postman_subject). \
			render(Context(self.get_context(recipient.mailer_profile, additional_context,
		                                    include_subject=False)))
	def get_postman_body_for(self, recipient, additional_context=None):
		return Template(self.postman_body).render(
			Context(self.get_context(recipient.mailer_profile, additional_context))
		)

	def get_context(self, recipient, additional_context=None, include_subject=True):
		if recipient.pk in self._contexts.keys():
			return self._contexts[recipient.pk]
		from tinkoff_merchant.models import Payment
		from tinkoff_merchant.consts import COFFEE_CUPS
		last_cup_payment = Payment.objects.filter(
			customer_key=str(recipient.user.pk),
			status__in=['CONFIRMED', 'AUTHORIZED'],
			receipt__receiptitem__category=COFFEE_CUPS
		).order_by('update_date').last()

		filtered_payments = self.recipients_filter.filter_user_payments(recipient.user)
		last_filtered_payment = filtered_payments.last()
		last_filtered_payment_category = last_filtered_payment.item_category


		next_after_payment_activation = None
		if last_cup_payment:
			from home.models import UserLesson
			activated_lesson_number = last_cup_payment.closest_activation
			activated_lesson_number = activated_lesson_number != '-' and int(activated_lesson_number)
			if activated_lesson_number:
				next_after_payment_activation = UserLesson.objects.get(lesson__lesson_number=activated_lesson_number, user=recipient.user)
		if recipient.user.first_name:
			name = recipient.user.first_name
		else:
			name = recipient.user.username
		context = dict(
			domain="www.le-francais.ru",
			user=recipient.user,
			profile=recipient,
			last_payment={
				'date': last_cup_payment.update_date if last_cup_payment else None,
				'cups_count': sum(
					item.site_quantity for item in last_cup_payment.items()) if last_cup_payment else 0,
			},
			filtered_payments=filtered_payments,
			last_filtered_payment=last_filtered_payment,
			last_filtered_payment_category=last_filtered_payment_category,
			unsubscribe_url=recipient.get_unsubscribe_url(),
			first_name=recipient.user.first_name,
			name=name,
			cups_quantity=recipient.user.cups_amount,
			next_after_payment_activation=next_after_payment_activation,
			COFFEE_CUPS='coffee_cups',
			LESSON_TICKETS='tickets',
			DONATIONS='donations',
		)
		if include_subject:
			context['subject'] = self.get_subject_for(recipient, additional_context)
		if additional_context:
			for k, v in additional_context.items():
				context[k]=v
		self._contexts[recipient.pk] = context
		return context


class MessageLogManager(models.Manager):
	def log(self, message:Message, recipient:User, result_code:int, log_message=""):
		return self.create(
			message_id=message.pk,
			recipient_id=recipient.pk,
			result=result_code,
			log_message=log_message
		)

	# TODO purge logs command and method
	def purge_logs(self):
		...


class MessageLog(models.Model):
	RESULT_SUCCESS = 1
	RESULT_FAILURE = 2
	RESULT_DIDNT_SEND = 3
	RESULT_POSTMAN_SUCCESS = 4
	RESULT_CHOICES = [
		(RESULT_SUCCESS, 'Success'),
		(RESULT_FAILURE, 'Failure'),
		(RESULT_DIDNT_SEND, "Didn't send"),
		(RESULT_POSTMAN_SUCCESS, "Success(P)")
	]
	RESULTS_SUCCESS = [RESULT_SUCCESS, RESULT_POSTMAN_SUCCESS]
	RESULTS_FAILURE = [RESULT_FAILURE, RESULT_DIDNT_SEND]
	message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True)
	recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	sent_datetime = models.DateTimeField(auto_now_add=True)
	result = models.IntegerField(choices=RESULT_CHOICES, default=RESULT_DIDNT_SEND)
	log_message = models.TextField(null=True, blank=True)

	objects = MessageLogManager()

	def __str__(self):
		return f'{self.message}'
