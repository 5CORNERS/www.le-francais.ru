from bulk_update import helper as update_helper
from django.core.management import BaseCommand
from django.db.models import Q

from le_francais_dictionary.models import Verb, VerbForm


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--rewrite', action='store_true', dest='rewrite')

    def handle(self, *args, **options):
        verbs_to_update = []
        forms_to_update = []
        verbs_query = Verb.objects.all()
        forms_query = VerbForm.objects.all()
        if not options['rewrite']:
            verbs_query = verbs_query.filter(Q(audio_url__isnull=True)|Q(translation_audio_url__isnull=True))
            forms_query = forms_query.filter(Q(audio_url__isnull=True)|Q(translation_audio_url__isnull=True))
        for verb in verbs_query:
            verbs_to_update.append(verb.to_voice(save=False))
            print(verb.verb, verb.audio_url, verb.translation_audio_url, sep='\t')
        for form in forms_query:
            forms_to_update.append(form.to_voice(save=False))
            print(form.form, form.audio_url, form.translation_audio_url, sep='\t')
        update_helper.bulk_update(verbs_to_update)
        update_helper.bulk_update(forms_to_update)
