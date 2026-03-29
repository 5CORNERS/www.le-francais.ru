from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

class Command(BaseCommand):
    help = 'Sets has_donated flag to True for users specified by email or username'

    def add_arguments(self, parser):
        parser.add_argument('identifiers', nargs='+', type=str, help='Emails or usernames of users')

    def handle(self, *args, **options):
        User = get_user_model()
        identifiers = options['identifiers']
        
        updated_count = 0
        for identifier in identifiers:
            users = User.objects.filter(Q(email=identifier) | Q(username=identifier))
            if users.exists():
                for user in users:
                    if not user.has_donated:
                        user.has_donated = True
                        user.save(update_fields=['has_donated'])
                        self.stdout.write(self.style.SUCCESS(f'Successfully set has_donated for user: {user}'))
                        updated_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f'User {user} already has has_donated flag set'))
            else:
                self.stdout.write(self.style.ERROR(f'User not found for identifier: {identifier}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total users updated: {updated_count}'))
