from bulk_update.helper import bulk_update
from django.core.management import BaseCommand

from le_francais_dictionary.models import UserWordRepetition
from le_francais_dictionary.utils import create_or_update_repetition


def update_repetitions():
	repetitions = UserWordRepetition.objects.all()
	for r in repetitions:
		user_word_data = r.word.last_user_data(r.user)
		create_or_update_repetition(user_word_data)
	bulk_update(repetitions, update_fields=['time', 'repetition_date'])


class Command(BaseCommand):
	def handle(self, *args, **options):
		update_repetitions()
