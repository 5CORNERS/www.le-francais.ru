import csv
import json

from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('currencies.csv', 'r', encoding='utf') as csv_file:
            reader = csv.reader(csv_file, dialect=csv.excel)
            result = {}
            for row in reader:
                result[row[0]] = {'html':row[2], 'text':row[1]}
        with open('currencies.json', 'w', encoding='utf') as json_file:
            json.dump(result, json_file)
