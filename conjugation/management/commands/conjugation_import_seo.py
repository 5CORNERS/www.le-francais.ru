import csv

from django.core.management import BaseCommand
from django_bulk_update.helper import bulk_update

from conjugation.models import Verb, VerbSEO

from tqdm import tqdm


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'][0], 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, dialect=csv.excel)
            rows = list(csv_reader)

            verb_seo_objects = []
            for row in tqdm(rows):
                try:
                    infinitive, title, description = row
                except ValueError:
                    self.stderr.write('The CSV file does not have the expected number of columns.')
                try:
                    verb = Verb.objects.get(infinitive=infinitive)
                except Verb.DoesNotExist:
                    self.stderr.write(f'No Verb with infinitive "{infinitive}" found')
                    continue
                verb_seo, _ = VerbSEO.objects.get_or_create(verb=verb)
                verb_seo.title = title
                verb_seo.description = description
                verb_seo_objects.append(verb_seo)
            bulk_update(verb_seo_objects)

        for verb_seo in verb_seo_objects:
            print(verb_seo.verb.get_url())
