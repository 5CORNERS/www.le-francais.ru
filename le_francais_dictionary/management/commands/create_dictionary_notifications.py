from django.core.management import BaseCommand
from django.utils import timezone
from notifications.models import create_dictionary_notification
from le_francais_dictionary.models import UserDayRepetition, UserWordRepetition


class Command(BaseCommand):
	def handle(self, *args, **options):
		create_notifications()
		create_failed_notifications()


def create_notifications():
	now_repetitions = UserDayRepetition.objects.filter(datetime__lte=timezone.now()).exclude(repetitions__len=0, success=True)
	for r in now_repetitions:
		try:
			create_dictionary_notification(UserDayRepetition, r)
			r.success = True
			r.save()
		except:
			r.success = False
			r.save()
			print(f'Error creating notification {r.pk}')


def create_failed_notifications():
	deferred_repetitions = UserDayRepetition.objects.filter(
		success=False
	)
	for deferred_repetition in deferred_repetitions:
		for i, r_id in reversed(list(enumerate(deferred_repetition.repetitions))):
			word_repetition = UserWordRepetition.objects.get(pk=r_id)
			if word_repetition.repetition_datetime != deferred_repetition.datetime:
				deferred_repetition.repetitions.pop(i)
		if deferred_repetition.repetitions:
			create_dictionary_notification(UserDayRepetition, deferred_repetition)
		deferred_repetition.success = True
		deferred_repetition.save()
