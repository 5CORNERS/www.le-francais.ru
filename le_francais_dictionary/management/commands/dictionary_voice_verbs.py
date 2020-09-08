from bulk_update import helper as update_helper
from django.core.management import BaseCommand

from le_francais_dictionary.models import Verb


class Command(BaseCommand):
    def handle(self, *args, **options):
        verbs_to_update = []
        forms_to_update = []
        for verb in Verb.objects.prefetch_related('verbform_set').all():
            verbs_to_update.append(verb.to_voice(save=False))
            print(verb.verb, verb.audio_url, verb.translation_audio_url, sep='\t')
            for form in verb.verbform_set.prefetch_related('verb', 'verb__verbform_set').all():
                forms_to_update.append(form.to_voice(save=False))
                print(form.form, form.audio_url, form.translation_audio_url, sep='\t')
        update_helper.bulk_update(verbs_to_update)
        update_helper.bulk_update(forms_to_update)
