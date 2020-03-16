from django.core.management import BaseCommand

from custom_user.models import User
from le_francais_dictionary.models import UserWordData, UserWordRepetition, get_repetition_words_query, Word


def check_user(user:User):
	print(user)
	to_del = []
	for word in get_repetition_words_query(user):
		if word.group is not None:
			new_word = Word.objects.filter(userdata__user=user, group=word.group).distinct().order_by('-userwordrepetition__time')
			if new_word.exists() and new_word.first() != word:
				to_del.append(word)
				print(word,'---', new_word.first())
	for word in to_del:
		UserWordRepetition.objects.filter(user=user, word=word).delete()

class Command(BaseCommand):
	def handle(self, *args, **options):
		for user in User.objects.filter(flash_cards_data__isnull=False).distinct():
			check_user(user)
