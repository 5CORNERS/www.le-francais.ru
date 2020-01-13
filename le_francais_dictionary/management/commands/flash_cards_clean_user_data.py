import datetime
import sys

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone

from le_francais_dictionary.models import UserWordData, Word, \
	UserWordRepetition
from le_francais_dictionary.utils import create_or_update_repetition

User = get_user_model()


class LoggingPrinter:
    def __init__(self, filename):
        self.out_file = open(filename, "a")
        self.old_stdout = sys.stdout
        sys.stdout = self
    def write(self, text):
        self.old_stdout.write(text)
        self.out_file.write(text)
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout


class Command(BaseCommand):
	def handle(self, *args, **options):
		with LoggingPrinter('flash_cards_clean_user_data.log'):
			print(f'========================================================\n'
			      f'Starting user data cleaning -- {datetime.datetime.now()}\n'
			      f'========================================================')
			for user in User.objects.filter(flash_cards_data__isnull=False).distinct():
				print(f'Cleaning User: {user}')
				for word in Word.objects.filter(userdata__user=user).distinct():
					print(f'Word: {word.word} -- {word.cd_id}')
					next_repeat_datetime = timezone.make_aware(datetime.datetime.min)
					repeat_time = None
					for user_word_data in UserWordData.objects.filter(
							user=user, word=word).order_by('datetime'):
						if user_word_data.datetime < next_repeat_datetime:
							print(f'DELETING {user_word_data} ++++ {user_word_data.datetime} < {next_repeat_datetime}')
							user_word_data_pk = user_word_data.pk
							user_word_data.delete()
							print(f'UserWordData {user_word_data_pk} was deleted')
						else:
							current_datetime, time = user_word_data.get_tz_aware_repetition_datetime_and_time()
							if current_datetime:
								next_repeat_datetime, repeat_time = current_datetime, time
							else:
								continue
					if repeat_time is not None and next_repeat_datetime != timezone.make_aware(datetime.datetime.min):
						if UserWordRepetition.objects.filter(user=user, word=word).exists():
							repetition = UserWordRepetition.objects.get(user=user, word=word)
							need_update = False
							if repetition.time != repeat_time:
								print(f'New time is {repeat_time}')
								need_update = True
							if repetition.repetition_datetime != next_repeat_datetime:
								print(f'New datetime is {next_repeat_datetime}')
								need_update = True
							if need_update:
								print(f'Updating {repetition}')
								repetition.time = repeat_time
								repetition.repetition_datetime = next_repeat_datetime
								repetition.save()
								print(
									f'UserWordRepetition {repetition.pk} was updated')
						else:
							print(f'Cant\'t find repetition {user} -- {word} -- {next_repeat_datetime} -- {repeat_time}')
							repetition = create_or_update_repetition(user.pk, word.pk, next_repeat_datetime, repeat_time)
							print(f'UserWordRepetition {repetition.pk} was created')
