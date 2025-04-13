from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from le_francais_dictionary.consts import REPETITIONS_OVERFLOW_COUNT
from le_francais_dictionary.models import UserWordRepetition, get_repetition_words_query

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

def annotate_users():
    users_with_repetitions = UserWordRepetition.objects.values("user").distinct().annotate(

    )