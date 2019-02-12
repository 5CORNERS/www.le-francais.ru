from django.core.management import BaseCommand
from conjugation.models import Verb

class Command(BaseCommand):
    def handle(self, *args, **options):
        s = ""
        for v in Verb.objects.all():
            print(v.infinitive)
            v.construct_conjugations()
            s +=str(v.infinitive) +  '\t' + str(v.conjugations["participle"]["past-participle"][0]) + "\n"
        open("verb-participle.tsv",'w',encoding='utf-8').write(s)