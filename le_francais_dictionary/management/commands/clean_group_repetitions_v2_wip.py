from datetime import datetime

from django.core.management import BaseCommand
from django.utils import timezone

from custom_user.models import User
from le_francais_dictionary.models import UserWordData, UserWordRepetition, get_repetition_words_query, Word


def check_user(user:User):
	print(user)
	to_del = []
	for word in get_repetition_words_query(user):
		if word.group is not None:
			word_to_stay = UserWordRepetition.objects.filter(user=user, word__group=word.group).order_by('repetition_datetime').values_list('word_id', flat=True).last()
			to_del += UserWordRepetition.objects.filter(user=user, word__group=word.group).exclude(word_id=word_to_stay).values_list('id', flat=True)

	print(to_del)

class Command(BaseCommand):
	def handle(self, *args, **options):
		for user in User.objects.filter(flash_cards_data__isnull=False).distinct():
			check_user(user)
