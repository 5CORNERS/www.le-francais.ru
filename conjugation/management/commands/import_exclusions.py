from django.core.management.base import BaseCommand
import pandas as pd
from conjugation.models import Verb as V

file_path = 'conjugation/data/Lists of Exclutions and Inclutions.csv'

def table_as_dict(csv_filepath):
    pd_data = pd.read_csv(open(csv_filepath,'r',encoding='utf-8'))
    return pd_data.to_dict()




class Command(BaseCommand):
    def handle(self, *args, **options):
        d = table_as_dict(file_path)
        0
