from django.core.management import BaseCommand
from conjugation.models import Verb as V, Template as T
import pandas as pd

PERSONS=[11,12,13,21,22,23]

def import_table():
    csv = open('conjugation/data/Table de colorisation.csv', 'r', encoding='utf-8')
    table = pd.read_csv(csv)
    verb_table = []
    for i in range(len(table.to_dict()['verb'])):
        verb_row = {
            'verb': table['verb'][i],
            11: table['11'][i],
            12: table['12'][i],
            13: table['13'][i],
            21: table['21'][i],
            22: table['22'][i],
            23: table['23'][i],
        }
        verb_table.append(verb_row)
    return verb_table


def fix_position(table_positions, table_v):
    if table_positions == "0":
        return "0"

    real_positions = []
    main_part_len = len(table_v.main_part)

    table_positions = table_positions.split(',')
    for table_pos in table_positions:
        real_pos = int(table_pos) - main_part_len
        real_positions.append(real_pos)

    real_positions_str = ""
    for real_pos in real_positions:
        real_positions_str += str(real_pos)+','
    real_positions_str = real_positions_str[:-1] # выбрасываем последнюю запятую

    return real_positions_str


def fix_positions(table):
    new_table = []
    for row in table:
        new_row = {}
        verb = row['verb']
        new_row['verb'] = verb
        table_v = V.objects.get(infinitive=verb)
        new_row['template'] = table_v.template.name

        for person in PERSONS:
            table_positions = row[person]
            real_positions = fix_position(table_positions, table_v)
            new_row[person] = real_positions
        new_table.append(new_row)
    return new_table


def print_csv(new_table):
    s = ("TEMPLATE,VERB,11,12,13,21,22,23\n")
    for row in new_table:
        s_row = (row['template']+','+row['verb']+',\"'+row[11]+"\",\""+row[12]+"\",\""+row[13]+"\",\""+row[21]+"\",\""+row[22]+"\",\""+row[23]+"\""+'\n')
        s += s_row
    return s



class Command(BaseCommand):
    def handle(self, *args, **options):
        table = import_table()
        new_table = fix_positions(table)
        print(print_csv(new_table))
        with open("conjugation/data/new_color.csv",'w',encoding='utf-8') as f:
            f.write(print_csv(new_table))
