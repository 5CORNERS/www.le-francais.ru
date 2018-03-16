from django.core.management.base import BaseCommand
from conjugation.models import Verb

class Command(BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument('verb_infinitives', nargs='+', type=str)
    def handle(self,*args,**options):
        for infinitive in options['verb_infinitives']:
            pass
            

