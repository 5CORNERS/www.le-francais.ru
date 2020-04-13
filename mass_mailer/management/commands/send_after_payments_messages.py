import re
from email.utils import parseaddr
from typing import List, Tuple

from django.core.management import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.sql.datastructures import Join
from django.utils import timezone

from home.models import UserLesson
from mass_mailer.models import EmailSettings, Message, MessageLog, Profile
from django.contrib.auth import get_user_model

from tinkoff_merchant.models import Payment, Receipt, ReceiptItem

User = get_user_model()


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument(
			'-sn', '--settings-name',
			required=True,
			help='You need to specify an email settings name..',
			dest='settings_name'
		)
		parser.add_argument(
			'-sb', '--subject',
			default='Subject',
			dest='subject'
		)
		parser.add_argument(
			'-html', '--html',
			default='mass_mailer/templates/mass_mailer/auto_messages/after_payment.html',
			dest='html'
		)
		parser.add_argument(
			'-txt', '--txt',
			default='mass_mailer/templates/mass_mailer/auto_messages/after_payment.txt',
			dest='txt'
		)
		parser.add_argument(
			'-f', '--from',
			default='Le-francais.ru <support@le-francais.ru>',
			dest='from'
		)
		parser.add_argument(
			'-rt', '--reply-to',
			default='Le-francais.ru <support@le-francais.ru>',
			dest='reply_to'
		)

	def handle(self, *args, **options):
		settings = get_email_setting(options['settings_name'])
		message = create_message(
			settings=settings,
			subject=options['subject'],
			template_html=get_template_string(options['html']),
			template_txt=get_template_string(options['txt']),
			from_header=options['from'],
			reply_to_header=options['reply_to'],
		)
		send_message(message, filter_users_with_payments_with_activations(message))


def filter_users_with_payments_with_activations(message):
	users_payments_activations = []
	receipt_items = ReceiptItem.objects.select_related('receipt', 'receipt__payment').filter(
		receipt__payment__status__in=["AUTHORISED", "CONFIRMED"]
	).filter(
		receipt__payment__update_date__date=timezone.now().today()
	).filter(
		receipt__payment__update_date__lte=timezone.now() - timezone.timedelta(minutes=15)
	).order_by('receipt__payment__customer_key')

	users = User.objects.filter(
		pk__in=[receipt_item.receipt.payment.customer_key for receipt_item in
		        receipt_items]
	).order_by('id').exclude(
		pk__in=[log.recipient_id for log in MessageLog.objects.filter(
			Q(result=MessageLog.RESULT_SUCCESS) | Q(
				result=MessageLog.RESULT_DIDNT_SEND), message=message)]
	).exclude(
		pk__in=[p.user.pk for p in Profile.objects.filter(
			subscribed=False
		)]
	)

	user_lessons = UserLesson.objects.select_related('lesson').filter(user_id__in=[u.pk for u in users]).order_by('date')

	item: ReceiptItem
	for item in receipt_items:
		update_datetime = item.receipt.payment.update_date
		user = next((u for u in users if u.pk == int(item.receipt.payment.customer_key)), None)
		# Exclude users which already got this message
		if user is None:
			continue
		# Exclude users which has more than one payment
		if Payment.objects.filter(status__in=["AUTHORISED", "CONFIRMED"], customer_key=str(user.pk)).count() > 1:
			continue
		activation = next((ul for ul in user_lessons if ul.date > update_datetime and ul.user_id == user.pk), None)
		payment = item.receipt.payment
		cups_quantity = item.site_quantity
		users_payments_activations.append((user, payment, activation, cups_quantity))
	return users_payments_activations


def get_contexts(users, message):
	pass


def split_username_email(addr):
	username, email = parseaddr(addr)
	if not username:
		raise CommandError(f"Missing username in {addr}")
	return username, email


def get_email_setting(name:str):
	try:
		username, host_port = name.split("@", 1)
		host, port = host_port.split(":", 1)
		setting = EmailSettings.objects.get(username=username, host=host, port=port)
	except EmailSettings.DoesNotExist:
		print(f'Setting with name "{name}" does not exist!')
		raise
	return setting


def get_template_string(path) -> str:
	with open(path, 'r', encoding='utf-8') as f:
		template_string = f.read()
	return template_string


def create_message(settings, subject, template_html, template_txt,
                   reply_to_header, from_header) -> Message:
	message, created = Message.objects.get_or_create(name='__after_payments')
	message.email_settings = settings
	message.template_subject = subject
	message.template_html = template_html
	message.template_txt = template_txt
	message.reply_to_username, message.reply_to_email = split_username_email(
		reply_to_header)
	message.from_username, message.from_email = split_username_email(
		from_header)
	message.save()
	return message


def send_message(message: Message, users_payments_activations: List[Tuple[User, Payment, UserLesson, int]]) -> (int, int):
	contexts = {}
	for user, payment, activation, quantity in users_payments_activations:
		contexts[user.pk] = get_context(user, message, payment, activation, quantity)
	sent_count, errors_count = message.send(to=[user for user, *o in users_payments_activations], users_context=contexts)
	return sent_count, errors_count


def get_context(user, message, payment, next_after_payment_activation=None, quantity=1) -> dict:
	context = {
		"payment":payment,
		"next_after_payment_activation":next_after_payment_activation,
		"cups_quantity":quantity
	}
	return context
