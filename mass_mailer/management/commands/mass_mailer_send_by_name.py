from freezegun import freeze_time
from django.core.management import BaseCommand

from mass_mailer.models import Message


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        :type parser: argparse.ArgumentParser
        """
        parser.add_argument('-n', '--name', type=str, required=True,
                            help='Name of the message object', action='append')
        parser.add_argument('-t', '--time', type=str, required=False,
                            help='Set datetime', default=None)
    def handle(self, *args, **options):
        if options['time'] is not None:
            freezer = freeze_time(options['time'])
            freezer.start()

        for name in options['name']:
            message = Message.objects.get(name=name)
            print(message.send())
