from django.core.management import BaseCommand

from mass_mailer.models import Message


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        :type parser: argparse.ArgumentParser
        """
        parser.add_argument('-n', '--name', type=str, required=True,
                            help='Name of the message object', action='append')
    def handle(self, *args, **options):
        for name in options['name']:
            message = Message.objects.get(name=name)
            print(message.send())
