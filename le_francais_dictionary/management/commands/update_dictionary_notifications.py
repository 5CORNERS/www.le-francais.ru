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
		day_repetitions = UserDayRepetition.objects.filter(repetitions__contains=[notification.object_id], user=user_notification.user)
		if day_repetitions:
			notification.content_object = day_repetitions.first()
			quantity = len(day_repetitions.first().repetitions)
			notification.data['qty'] = message(quantity)
			notification.save()
			print(day_repetitions)


class Command(BaseCommand):
	def handle(self, *args, **options):
		update_notifications()
