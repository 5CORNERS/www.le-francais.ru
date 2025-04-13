from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone

from le_francais_dictionary.models import UserWordRepetition, get_repetition_words_query

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        users_counts = {}

        users_with_repetitions = UserWordRepetition.objects.values_list("user", flat=True).distinct()
        print(f"users_with_repetitions: {users_with_repetitions.count()}")
        for i, user in enumerate(User.objects.filter(id__in=users_with_repetitions)):
            print(f"{i}/{users_with_repetitions.count()}: {user.username}")
            c = get_repetition_words_query(user).count()
            users_counts[user.username] = c

        s = ""
        for username, count in sorted(users_counts.items(), key=lambda x: x[1], reverse=True):
            s += f"{count}\n"
            print(count)
        with open("repetitions_count.txt", "w") as f:
            f.write(s)