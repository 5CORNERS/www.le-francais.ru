from bulk_update.helper import bulk_update
from django.core.management import BaseCommand

from le_francais_dictionary.models import UserDayRepetition
from notifications.models import Notification, NotificationUser


def update_notifications():
	notifications = Notification.objects.filter(category=Notification.INTERVAL_REPETITIONS)
	for notification in notifications:
		user_notification = notification.notificationuser_set.first()
		day_repetitions = UserDayRepetition.objects.filter(repetitions__contains=[notification.object_id], user=user_notification.user)
		if day_repetitions:
			notification.content_object = day_repetitions.first()
			notification.data['qty'] = len(day_repetitions.first().repetitions)
			notification.save()
			print(day_repetitions)


class Command(BaseCommand):
	def handle(self, *args, **options):
		update_notifications()
