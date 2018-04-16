from django.core.management.base import BaseCommand
from conjugation.models import Template as T


def count(t):
    c = 0
    for mood in t.new_data.keys():
        for tense in t.new_data[mood].keys():
            for person in t.data[mood][tense]['p']:
                if isinstance(person['i'], list):
                    l = len(person['i'])
                else:
                    l = 1

                if c<l:
                    c = l
    return c


class Command(BaseCommand):
    def handle(self,*args,**options):
        for t in T.objects.all():
            print(t.name)
            t.forms_count = count(t)
            t.save()
