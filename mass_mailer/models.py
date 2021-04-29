import smtplib
from datetime import datetime
from ssl import socket_error

from django.db.models import Q
from django.utils import timezone
from typing import Tuple

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
from validate_email import validate_email

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
	subscribed = models.BooleanField(default=True)

	def get_unsubscribe_url(self):
		domain = 'www.le-francais.ru'
		return 'https://' + domain + reverse("mass_mailer:unsubscribe", kwargs={"key": self.key})

	def __str__(self):
		return str(self.user)


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
	USERS_WITHOUT_ACTIVATIONS = '0'
	USERS_WITH_PAYMENTS = '1'
	PAYMENTS_WITHOUT_ACTIVATIONS = '2'
	USERS_WITH_PAYMENTS_EQ1CUP = '3'
	USERS_WITH_PAYMENTS_GT1CUP = '4'
	FILTERS = [
		(USERS_WITHOUT_ACTIVATIONS, 'Users w/o activations'),
		(USERS_WITH_PAYMENTS, 'Users with payments'),
		(PAYMENTS_WITHOUT_ACTIVATIONS, 'Payments w/o activations'),
		(USERS_WITH_PAYMENTS_EQ1CUP, 'Users, which payed for 1 cup only'),
		(USERS_WITH_PAYMENTS_GT1CUP, 'Users, which payed for more than 1 cups'),
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

	has_name_for_emails = models.BooleanField(default=False)

	blacklist = models.ManyToManyField(to=User, blank=True)
	manual_email_list = models.TextField(max_length=1024, help_text='Comma-separated list of emails, for testing purposes.', default=None, null=True, blank=True)
	manual_blacklist = models.TextField(blank=True, null=True, default=None)
	ignore_subscriptions = models.BooleanField(default=False)
	send_once = models.BooleanField(default=True)
	send_to_not_validated = models.BooleanField(default=True)

	send_only_first = models.IntegerField(null=True, blank=True, default=None)
	do_not_send_to_pass_partout = models.BooleanField(default=False)

	do_not_send_to_gmail = models.BooleanField(default=False)
	do_not_send_to_yandex = models.BooleanField(default=False)
	do_not_send_to_mailru = models.BooleanField(default=False)
	do_not_send_to_comcast = models.BooleanField(default=False)

	def __str__(self):
		return self.name

	def get_recipients(self):
		from tinkoff_merchant.models import Payment
		recipients = User.objects.all()
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
						              payments_query]
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
							id__in=[int(p.customer_key) for p in payments])

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
							id__in=[int(p.customer_key) for p in payments]
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
							id__in=[int(p.customer_key) for p in payments]
						)
			if not self.ignore_subscriptions:
				recipients = recipients.exclude(pk__in=[p.user.pk for p in
				                                        Profile.objects.filter(
					                                        subscribed=False)])
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
			recipients = recipients.exclude(is_active=False).order_by('-date_joined')
			recipients = recipients.distinct()
		return recipients

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
				pk__in=[log.recipient_id for log in MessageLog.objects.filter(Q(result=MessageLog.RESULT_SUCCESS) | Q(result=MessageLog.RESULT_DIDNT_SEND), message=message)])
		if not self.send_to_not_validated:
			recipients = recipients.exclude(
				pk__in=MessageLog.objects.filter(
					Q(result=MessageLog.RESULT_FAILURE)|Q(result=MessageLog.RESULT_DIDNT_SEND),
					message=message).distinct().values_list('recipient_id', flat=True)
			)
		return recipients


class Message(models.Model):
	name = models.CharField(max_length=64, blank=True, null=True, unique=True)

	template_subject = models.CharField(max_length=64, blank=True)
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

	created_datetime = models.DateTimeField(auto_now_add=True)
	send_datetime = models.DateTimeField(null=True)

	list_unsubscribe_header = models.BooleanField(default=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._recipients = None

	def __str__(self):
		return f'{self.template_subject}'

	def get_reply_to_header(self):
		if self.reply_to_email:
			return [f'{self.reply_to_username} <{self.reply_to_email}>']
		return None

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
		if self._recipients is None:
			if self.recipients_filter:
				self._recipients = self.recipients_filter.get_recipients_for_message(
					message=self)
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

				email_message = EmailMultiAlternatives(
					subject=Template(self.template_subject).render(Context(data['context'])),
					from_email=f'{self.from_username} <{self.from_email}>',
					to=[f'"{data["name"]}" <{data["email"]}>'],
					headers=header,
					reply_to=self.get_reply_to_header(),
					body=Template(self.template_txt).render(Context(data['context']))
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
				except (socket_error, smtplib.SMTPSenderRefused,
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
			recipients = self.get_recipients()
		else:
			recipients = to
		sent_count = 0
		errors_count = 0
		if not recipients:
			return sent_count, errors_count
		if self.recipients_filter and self.recipients_filter.send_only_first:
			recipients = recipients[:self.recipients_filter.send_only_first]
		chunks = [recipients[x:x+self.email_settings.messages_per_connection] for x in range(0, len(recipients), self.email_settings.messages_per_connection)]
		for chunk in chunks:
			messages_with_recipients = []
			for recipient in chunk:
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
					continue
				header = {
					'Sender': f'{self.email_settings.get_sender_header()}',
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
				email_message = EmailMultiAlternatives(
					subject=self.get_subject_for(recipient.mailer_profile, additional_context),
					from_email=f'{self.from_username} <{self.from_email}>',
					to=[f'"{recipient.username}" <{recipient.email}>'],
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
					time.sleep(1)
				except (socket_error, smtplib.SMTPSenderRefused,
				        smtplib.SMTPRecipientsRefused,
				        smtplib.SMTPDataError,
				        smtplib.SMTPAuthenticationError) as error:
					MessageLog.objects.log(self, recipient, MessageLog.RESULT_FAILURE,
					                       log_message=str(error))
					errors_count += 1
					print(f"SMTP Error: {str(error)}")
			backend.close()
			time.sleep(self.email_settings.delay_between_connections)
		return sent_count, errors_count

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

	def get_context(self, recipient, additional_context=None, include_subject=True):
		from tinkoff_merchant.models import Payment
		last_payment = Payment.objects.filter(customer_key=str(recipient.user.pk), status__in=['CONFIRMED', 'AUTHORIZED']).order_by('update_date').last()

		next_after_payment_activation = None
		if last_payment:
			from home.models import UserLesson
			activated_lesson_number = last_payment.closest_activation
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
				'date': last_payment.update_date if last_payment else None,
				'cups_count': sum(
					item.site_quantity for item in last_payment.items()) if last_payment else 0
			},
			unsubscribe_url=recipient.get_unsubscribe_url(),
			first_name=recipient.user.first_name,
			name=name,
			cups_quantity=sum(
					item.site_quantity for item in last_payment.items()) if last_payment else 0,
			next_after_payment_activation=next_after_payment_activation
		)
		if include_subject:
			context['subject'] = self.get_subject_for(recipient, additional_context)
		if additional_context:
			for k, v in additional_context.items():
				context[k]=v
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
	RESULT_CHOICES = [
		(RESULT_SUCCESS, 'Success'),
		(RESULT_FAILURE, 'Failure'),
		(RESULT_DIDNT_SEND, "Didn't send")
	]
	message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True)
	recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	sent_datetime = models.DateTimeField(auto_now_add=True)
	result = models.IntegerField(choices=RESULT_CHOICES, default=RESULT_DIDNT_SEND)
	log_message = models.TextField(null=True, blank=True)

	objects = MessageLogManager()

	def __str__(self):
		return f'{self.message}'
