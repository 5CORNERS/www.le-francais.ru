from django.core.management.base import BaseCommand

from custom_user.models import User
from pybb.models import Post, Topic
from postman.models import Message


class Command(BaseCommand):
    help = 'Delete user and move their posts, topics, and messages to the DELETED user'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='The username of the user to delete'
        )

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print('User with username "%s" does not exist' % username)
            return

        try:
            deleted_user = User.objects.get(username='DELETED')
        except User.DoesNotExist:
            deleted_user = User.objects.create_user(
                username='DELETED',
                email='deleted@le-francais.ru'
            )

        Post.objects.filter(user=user).update(user=deleted_user)
        Topic.objects.filter(user=user).update(user=deleted_user)
        Message.objects.filter(sender=user).update(sender=deleted_user)
        Message.objects.filter(recipient=user).update(recipient=deleted_user)

        user.delete()

        print('User "%s" deleted' % username)