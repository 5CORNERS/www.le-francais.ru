from django.core.management import BaseCommand, CommandError
from pybb.models import Topic
from datetime import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('from', type=int, nargs='+')
        parser.add_argument('to', type=int, nargs='+')
        parser.add_argument('-k', action='store_true', dest='k', default=False, help='Do not change firs post create_date')

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
            if not options['k']:
                first_post = to_topic.head
                first_post.created = datetime(2011, 1 , 1)
                first_post.save()
            for post in from_topic.posts.all():
                post.topic = to_topic
                post.save()
            from_topic.delete()
            to_topic.update_counters()
            print('Done!')
        else:
            pass