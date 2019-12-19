from bulk_update.helper import bulk_update
from django.core.management import BaseCommand

from le_francais_dictionary.models import UserDayRepetition
from notifications.models import Notification, NotificationUser

def message(n, form1=' новое слово', form2=' новых слова', form5=' новых слов'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)

def update_notifications():
	notifications = Notification.objects.filter(category=Notification.INTERVAL_REPETITIONS)
	for notification in notifications:
		user_notification = notification.notificationuser_set.first()
		day_repetitions = UserDayRepetition.objects.filter(
			user=user_notification.user,
			datetime__day=notification.datetime_creation.day
		)
		day_repetition = day_repetitions.order_by('datetime').first()
		if day_repetitions.count() > 1:
			print(f'ERROR! User {user_notification.user} have more than one day repetition on {notification.datetime_creation.date()}\n'
			      f'Using first day repetition {day_repetition}')
			notification.content_object = day_repetition
			quantity = len(day_repetition.repetitions)
			notification.data['quantity_message'] = 'появилось ' + message(quantity)
			notification.save()
			print(day_repetition)
		elif day_repetitions.count() == 0:
			print(f'ERROR! User {user_notification.user} has no day repetitions on {notification.datetime_creation.date()}\n'
			      f'Adding neutral quantity message')
			notification.data['quantity_message'] = 'появились новые слова'
			notification.save()


class Command(BaseCommand):
	def handle(self, *args, **options):
		update_notifications()
