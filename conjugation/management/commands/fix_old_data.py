from django.core.management import BaseCommand
from conjugation.models import Template as T

import re


def remove_bold(ending):
    if ending == None:
        return None
    ending = re.sub('<b>','',ending)
    ending = re.sub('</b>', '', ending)
    return ending


class Command(BaseCommand):
    def handle(self, *args, **options):
        for t in T.objects.all():
            print(t)
            for mood in t.data.keys():
                for tense in t.data[mood].keys():
                    for i, person in enumerate(t.data[mood][tense]['p']):
                        endings = person['i']
                        if isinstance(endings, list):
                            for index,ending in enumerate(endings):
                                new_ending = remove_bold(ending)
                                endings[index] = new_ending
                        else:
                            ending = endings
                            new_ending = remove_bold(ending)
                            endings = new_ending
                        t.data[mood][tense]['p'][i]['i'] = endings
                        0
                        t.save()