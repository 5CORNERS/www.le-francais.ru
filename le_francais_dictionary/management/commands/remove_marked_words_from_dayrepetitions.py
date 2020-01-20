from django.core.management import BaseCommand

from le_francais_dictionary.models import UserDayRepetition, \
	UserWordRepetition, UserWordIgnore


class Command(BaseCommand):
	def handle(self, *args, **options):
		for day_repetition in UserDayRepetition.objects.all():
			for pk in reversed(day_repetition.repetitions):
				repetition = UserWordRepetition.objects.get(pk=pk)
				if UserWordIgnore.objects.filter(user=day_repetition.user, word=repetition.word).exists():
					print(f'{day_repetition.user} -- {repetition.word}')
					day_repetition.repetitions.remove(pk)
					print(f'{pk} <= {day_repetition.repetitions}')
