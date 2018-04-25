from django.core.management import BaseCommand
from conjugation.models import Verb as V, ReflexiveVerb  as RV

class Command(BaseCommand):
    def handle(self, *args, **options):
        for v in V.objects.all():
            if v.reflexive:
                reflexive_verb = RV.objects.get_or_create(infinitive=v.reflexive)
                reflexive_verb.create_no_accents()
                reflexive_verb.save()