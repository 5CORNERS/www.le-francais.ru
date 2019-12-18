from bulk_update.helper import bulk_update
from django.core.management import BaseCommand

from le_francais_dictionary.models import UserWordRepetition
from le_francais_dictionary.utils import create_or_update_repetition


def update_repetitions():
	repetitions = UserWordRepetition.objects.all()
	for r in repetitions:
		r.update(save=False)
		print(r)
	bulk_update(repetitions, update_fields=['time', 'repetition_date', 'repetition_datetime'])


class Command(BaseCommand):
	def handle(self, *args, **options):
		update_repetitions()
