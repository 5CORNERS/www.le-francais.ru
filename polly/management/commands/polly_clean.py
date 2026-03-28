from django.core.management import BaseCommand
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist

from polly.models import PollyTask
from conjugation.models import PollyAudio
from le_francais_dictionary.models import Word, WordTranslation, Verb, VerbForm, UnifiedWord

class Command(BaseCommand):
    def collect_related_pks(self):
        related_models = [
            (PollyAudio, 'polly__pk'),
            (Word, 'polly__pk'),
            (WordTranslation, 'polly__pk'),
            (Verb, 'polly__pk'),
            (Verb, 'translation_polly__pk'),
            (VerbForm, 'polly__pk'),
            (VerbForm, 'translation_polly__pk'),
        ]

        pks = set()
        for model, field in related_models:
            try:
                queryset = model.objects.filter(**{field.replace('__pk', '__isnull'): False}).order_by('pk')
                paginator = Paginator(queryset, 1000)
                for page_num in paginator.page_range:
                    batch = paginator.page(page_num).object_list
                    pks.update(batch.values_list(field, flat=True))
            except ObjectDoesNotExist as e:
                self.stderr.write(f"Error collecting PKs from {model.__name__}: {e}")
        return pks

    def collect_audio_urls(self):
        url_fields = [
            (Word, '_polly_url'),
            (WordTranslation, '_polly_url'),
            (Verb, 'audio_url'),
            (Verb, 'translation_audio_url'),
            (VerbForm, 'audio_url'),
            (VerbForm, 'translation_audio_url'),
            (UnifiedWord, 'word_polly_url'),
            (UnifiedWord, 'translation_polly_url'),
        ]

        urls = set()
        for model, field in url_fields:
            try:
                queryset = model.objects.filter(**{f"{field}__isnull": False}).order_by('pk')
                paginator = Paginator(queryset, 1000)
                for page_num in paginator.page_range:
                    batch = paginator.page(page_num).object_list
                    urls.update(batch.values_list(field, flat=True))
            except ObjectDoesNotExist as e:
                self.stderr.write(f"Error collecting URLs from {model.__name__}: {e}")
        return urls

    def handle(self, *args, **options):
        try:
            self.stdout.write("Gathering related PKs...")
            polly_related_pks = self.collect_related_pks()

            self.stdout.write("Gathering URLs...")
            all_audio_urls = self.collect_audio_urls()

            not_related_polly_tasks = PollyTask.objects.exclude(pk__in=polly_related_pks)

            total_with_urls = PollyTask.objects.filter(url__in=all_audio_urls).count()
            not_related_with_urls = not_related_polly_tasks.filter(url__in=all_audio_urls).count()

            self.stdout.write(f"Total PollyTasks with URLs: {total_with_urls}")
            self.stdout.write(f"Not related PollyTasks with URLs: {not_related_with_urls}")

        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")
            raise