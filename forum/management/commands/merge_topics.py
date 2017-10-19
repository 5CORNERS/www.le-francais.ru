from django.core.management import BaseCommand, CommandError
from pybb.models import Topic
from datetime import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('from', type=int, nargs='+')
        parser.add_argument('to', type=int, nargs='+')

    def handle(self, *args, **options):
        id_from = options['from'][0]
        id_to = options['to'][0]
        try:
            from_topic = Topic.objects.get(id = id_from)
        except:
            raise CommandError("\nCouldn't find topic with this id " + str(id_from))
        try:
            to_topic = Topic.objects.get(id = id_to)
        except:
            raise CommandError("\nCouldn't find topic with this id " + str(id_to))

        confirm = input("\nDo you want to transfer all posts from topic " + str(id_from) + ' to topic ' + str(id_to) + '\nY/N: ')

        if confirm == 'Y' or confirm == 'y':
            first_topic = to_topic.head
            first_topic.created = datetime(2011, 1 , 1)
            first_topic.save()
            for post in from_topic.posts.all():
                post.topic = to_topic
                post.save()
            from_topic.delete()
            to_topic.update_counters()
            print('Done!')
        else:
            pass