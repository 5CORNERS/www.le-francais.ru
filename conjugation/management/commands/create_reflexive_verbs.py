from django.core.management import BaseCommand

from conjugation.models import Verb as V, ReflexiveVerb as RV


class Command(BaseCommand):
    def handle(self, *args, **options):
        for v in V.objects.all():
            if v.can_reflexive or v.reflexive_only:
                reflexive_infinitive = "se "+v.infinitive if v.infnitive_first_letter_is_vowel() else "s'"+v.infinitive
                rv, created = RV.objects.get_or_create(infinitive=reflexive_infinitive, verb=v)
                rv.create_no_accents()
                rv.save()
                print(rv.infinitive)
