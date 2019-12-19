import pytz
from django.core.management import BaseCommand
from django.utils import timezone

from le_francais_dictionary.models import UserWordRepetition, UserDayRepetition


class Command(BaseCommand):
	def handle(self, *args, **options):
		for repetition in UserWordRepetition.objects.all():
			if repetition.repetition_datetime is None:
				repetition.update(save=True)
			day_repetition, created = UserDayRepetition.objects.get_or_create(
				user=repetition.user,
				datetime=repetition.repetition_datetime
			)
			if not repetition.pk in day_repetition.repetitions:
				day_repetition.repetitions.append(repetition.pk)
				day_repetition.save()
				print(day_repetition)
