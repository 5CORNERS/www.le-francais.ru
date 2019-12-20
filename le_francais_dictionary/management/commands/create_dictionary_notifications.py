from django.core.management import BaseCommand
from django.utils import timezone
from notifications.models import create_dictionary_notification
from le_francais_dictionary.models import UserDayRepetition


class Command(BaseCommand):
	def handle(self, *args, **options):
		create_notifications()


def create_notifications():
	now_repetitions = UserDayRepetition.objects.filter(
		datetime__day=timezone.now().day, datetime__hour=timezone.now().hour)
	for r in now_repetitions:
		try:
			create_dictionary_notification(UserDayRepetition, r)
			r.success = True
			r.save()
		except:
			r.success = False
			r.save()
			print(f'Error creating notification {r.pk}')
