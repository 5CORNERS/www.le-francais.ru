from django.core.management import BaseCommand
from django.db.models import Q

from custom_user.models import LogMessage, User
from home.models import UserLesson
from tinkoff_merchant.models import Payment as TinkoffPayment, ReceiptItem as TinkoffItem

def print_activities():
	activities = []
	print(1)
	for logmessage in LogMessage.objects.select_related('user').filter(user__isnull=False):
		email = logmessage.user.email
		datetime = logmessage.datetime.strftime('%Y-%m-%d')
		action_type = logmessage.get_type_display() or 'Download'
		lesson_num = logmessage.message if logmessage.type == 1 else logmessage.message.split(' ')[-1]
		if next((x for x in activities if x[1] == email and  x[2] == action_type and x[0] == datetime and x[3] == lesson_num), False):
			continue
		activities.append((
			datetime,
			email,
			action_type,
			lesson_num,
			'',
			''
		))
	print(2)
	userlessons = UserLesson.objects.all().prefetch_related('user', 'lesson').order_by('date')
	for userlesson in userlessons:
		activities.append((
			userlesson.date.strftime('%Y-%m-%d'),
			userlesson.user.email,
			'Activation',
			userlesson.lesson.lesson_number,
			userlesson.remains or '',
			''
		))
	print(3)
	users = User.objects.all()
	for item in TinkoffItem.objects.select_related('receipt', 'receipt__payment').filter(
			Q(receipt__payment__status='CONFIRMED') | Q(receipt__payment__status='AUTHORIZED')
	).distinct():
		lesson_number = next((x.lesson.lesson_number for x in userlessons if x.date > item.receipt.payment.creation_date))
		email = next((x.email for x in users if x.pk == int(item.receipt.payment.customer_key)), '')
		activities.append((
			item.receipt.payment.creation_date.strftime('%Y-%m-%d'),
			email,
			'Payment',
			lesson_number,
			item.site_quantity,
			item.category.split('_')[0],
		))
	activities = sorted(activities, key=lambda tup: tup[0])
	print('DATE', 'USER', 'ACTION', 'LESSON_NUM', 'CUPS', 'ITEM', sep='\t')
	for a, b, c, d, e, f in activities:
		print(a, b, c, d, e, f, sep='\t')

class Command(BaseCommand):
	def handle(self, *args, **options):
		print_activities()
