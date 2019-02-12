from django.core.management.base import BaseCommand

from conjugation.models import Template as T, Verb as V
from conjugation.views import Person
import re

RED_ENDINGS = {
    # 'infinitive_infinitive-present': [
    #     ['er', 'ir', 'ïr', 're']
    # ],
    'indicative_present': [
        ['e', 's', 'x'],
        ['es', 's', 'x'],
        ['e', 't', 'd'],
        ['ons'],
        ['ez', 'es'],
        ['ent', 'ont'],
    ],
    'indicative_imperfect': [
        ['ais'],
        ['ais'],
        ['ait'],
        ['ions'],
        ['iez'],
        ['aient'],
    ],
    'indicative_future': [
        ['ai'],
        ['as'],
        ['a'],
        ['ons'],
        ['ez'],
        ['ont'],
    ],
    'indicative_simple-past': [
        ['ai', 'is', 'ïs', 'us', 'ûs', 'ins'],
        ['as', 'is', 'ïs', 'us', 'ûs', 'ins'],
        ['a', 'it', 'ït', 'ut', 'ût', 'int'],
        ['âmes', 'îmes', 'ïmes', 'ûmes', 'înmes'],
        ['âtes', 'îtes', 'ïtes', 'ûtes', 'întes'],
        ['èrent', 'irent', 'ïrent', 'urent', 'ûrent', 'inrent'],
    ],
    'conditional_present': [
        ['ais'],
        ['ais'],
        ['ait'],
        ['ions'],
        ['ez'],
        ['aient'],
    ],
    'subjunctive_present': [
        ['e'],
        ['es'],
        ['e', 't'],
        ['ions','yons'],
        ['iez', 'yez'],
        ['ent'],
    ],
    'subjunctive_imperfect': [
        ['se'],
        ['ses'],
        ['t'],
        ['sions'],
        ['siez'],
        ['sent'],
    ],
    'imperative_imperative-present': [
        ['e', 'is', 's', 'x'],
        ['issons', 'ons', ],
        ['issez', 'ez', 'es', ],
    ],
    'participle_present-participle': [
        ['ant'],
    ],
    'participle_past-participle': [
        ['é', 'i', 'ï', 'it', 'is', 'u', 'û', 't', 'os', 'us'],
        ['és', 'is', 'ïs', 'it', 'us', 'ûs', 'ts', 'os'],
        ['ée', 'ie', 'ïe', 'ite', 'ise', 'ue', 'ûe', 'te', 'ose', 'use'],
        ['ées', 'ies', 'ïes', 'ites', 'ises', 'ues', 'ûes', 'tes', 'oses', 'uses'],
    ]
}
NO_RED_IN_II = ['tendre', 'mettre', 'prendre', 'battre', 'moudre', 'coudre', 'asseoir', 'sourdre', ]
RIGHT_VERB = ['hurler', 'voyager', 'violacer', 'vulnérer', 'hoqueter', 'taveler', 'hongroyer', 'zézayer', 'videler',
              'végéter', 'succéder', 'vener', 'surélever', 'haleter', 'sécher', 'rengréner', 'siéger', 'perpétrer',
              'héler', 'subdéléguer', 'zébrer', 'réaléser', 'réséquer', 'sursemer', 'écrémer', 'redépecer',
              'réintégrer', 'soupeser', 'renvoyer', 'langueyer', 'régler', 'régner', 'aller', 'brumasser', 'enfiévrer',
              'ester', 'exécrer', 'harceler', 'hébéter', 'receper', 'recéper', 'référencier', 'sevrer', ]


def check_red_end(t_end: str, r_ends: list):
    """t_end - окончание темплейта, r_ends - список 'правильных' окончаний"""
    t_end_len = t_end.__len__()
    for r_end in r_ends:
        if t_end_len < r_end.__len__():
            continue
        else:
            if t_end.endswith(r_end):
                return t_end.rsplit(r_end,1)[0], r_end
    return t_end, None


def print_wrong_ends():
    c = 0
    for t in T.objects.all():
        no_red_end = False
        for mood_tense in RED_ENDINGS:
            mood, tense = mood_tense.split('_')
            for n, r_ends in enumerate(RED_ENDINGS[mood_tense]):  # итерируемся по лицам соответсвенно темплейту
                t_ends = t.data[mood][tense]['p'][n]['i']  # получаем окончания (если их несколько) из темплейта
                if t_ends == None:  # если окончания в таком лице/роде не существует
                    continue
                if isinstance(t_ends, list):  # если окончаний больше одного
                    forms = []
                    for t_end in t_ends:
                        forms.append(check_red_end(t_end, r_ends))
                else:
                    t_end = t_ends
                    not_end, r_end = check_red_end(t_end, r_ends)
                    forms = [(not_end, r_end,)]
                for form_i, form in enumerate(forms):
                    if form[1] == None:
                        no_red_end = True
                        error = "Template: " + t.name + '\nCan not find red end:\n\tmood: ' + mood + '\n\ttense: ' + tense + '\n\ti: ' + str(
                            n) + '\n\tform: ' + str(form_i) + '\n\t' + str(form)
                        r_ends = 'Given endings: ' + str(r_ends)
                        print(error + '\n' + r_ends, end='\n\n')
        if no_red_end:
            c += 1
    print(c)


def fix_null():
    for t in T.objects.all():
        data = t.data
        for mood in data:
            for tense in data[mood]:
                new_p = []
                for i in (data[mood][tense]['p']):
                    if i == None:
                        new_p.append({'i': None})
                    else:
                        new_p.append(i)
                data[mood][tense]['p'] = new_p
        t.data = data
        t.save()


def print_list_imperative():
    V_LIST = [
        'grasseyer',
        'aller',
        'brumasser',
        'ester',
        'référencier'
    ]
    PERSONS = ['person_I_S_M', 'person_II_S_M', 'person_III_S_M', 'person_I_P_M', 'person_II_P_M', 'person_III_P_M', ]
    # with open('verb_list','w',encoding='utf-8') as f:
    for verb in V_LIST:
        print('<tr><td>' + verb + '</td>', end='')
        v = V.objects.get(infinitive=verb)
        for person_name in PERSONS:
            verb_conjugation = Person(v, mood_name='indicative', tense_name='present', person_name=person_name)
            if verb_conjugation.part_1 == '':
                verb_conjugation.part_1 = ''
                verb_conjugation.part_2 = '-'
            print('<td>' + verb_conjugation.part_1 + '<b>' + verb_conjugation.part_2 + '</b>' + '</td>', end='')
        print('</tr>')

        print()


def import_table():
    import pandas as pd
    csv = open('conjugation/data/Fixed Color.csv', 'r', encoding='utf-8')
    table = pd.read_csv(csv)
    verb_table = []
    for i in range(len(table.to_dict()['VERB'])):
        verb_row = {
            'verb': table['VERB'][i],
            11: table['11'][i],
            12: table['12'][i],
            13: table['13'][i],
            21: table['21'][i],
            22: table['22'][i],
            23: table['23'][i],
        }
        verb_table.append(verb_row)
    return verb_table


def real_pos(str:str, v):
    positions_in_str = str.split(',')
    positions = []
    for pos in positions_in_str:
        pos = int(pos) - 1
        positions.append(pos)
    return positions


def get_ending(t_endings):
    if isinstance(t_endings, list):
        return t_endings
    elif t_endings == None:
        return None
    else:
        return t_endings


def make_blue(table):
    PERSONS_MAPPING = {11:0,12:1,13:2,21:3,22:4,23:5}
    MOOD_TENSE = ('indicative','present')
    for row in table:
        verb = row['verb']
        print(verb)
        v = V.objects.get(infinitive=verb)
        t = v.template
        for person in PERSONS_MAPPING:
            # print('\t' + str(person)+' - ', end='')
            table_positions = row[person]
            if table_positions == None or table_positions == '0':
                # print()
                continue
            positions = real_pos(table_positions, v)
            t_endings = get_ending(t.data[MOOD_TENSE[0]][MOOD_TENSE[1]]['p'][PERSONS_MAPPING[person]]['i'])
            if isinstance(t_endings, list):
                t.new_data[MOOD_TENSE[0]][MOOD_TENSE[1]]['p'][PERSONS_MAPPING[person]]['i'] = []
                for n,t_ending in enumerate(t_endings):
                    if t_ending == None:
                        # print()
                        continue
                    for pos in reversed(positions):
                        t_ending = t_ending[:pos] + '<i>' + t_ending[pos] + '</i>' + t_ending[pos+1:]
                    t_ending = re.sub('\<\/i\>\<i\>', '', t_ending)
                    t.new_data[MOOD_TENSE[0]][MOOD_TENSE[1]]['p'][PERSONS_MAPPING[person]]['i'].append(t_ending)
            else:
                t.new_data[MOOD_TENSE[0]][MOOD_TENSE[1]]['p'][PERSONS_MAPPING[person]]['i'] = []
                t_ending = t_endings
                if t_ending == None:
                    # print()
                    continue
                for pos in reversed(positions):
                    t_ending = t_ending[:pos] + '<i>' + t_ending[pos] + '</i>' + t_ending[pos + 1:]
                t_ending = re.sub('\<\/i\>\<i\>', '', t_ending)
                t.new_data[MOOD_TENSE[0]][MOOD_TENSE[1]]['p'][PERSONS_MAPPING[person]]['i'].append(t_ending)
            t.save()



def make_red():
    for t in T.objects.all():
        print(t.name)
        for mood_tense in RED_ENDINGS:
            mood, tense = mood_tense.split('_')
            for person, red_endings in enumerate(RED_ENDINGS[mood_tense]):
                if mood == 'indicative' and tense == 'present':
                    t_endings = t.new_data[mood][tense]['p'][person]['i']
                    t_endings = get_ending(t_endings)
                else:
                    t.new_data[mood][tense]['p'][person]['i'] = t.data[mood][tense]['p'][person]['i']
                    t_endings = t.data[mood][tense]['p'][person]['i']
                    t_endings = get_ending(t_endings)

                if isinstance(t_endings, list):
                    for n,t_ending in enumerate(t_endings):
                        if t_ending == None:
                            continue
                        t_ending, red_ending = check_red_end(t_ending, red_endings)
                        if red_ending != None:
                            t.new_data[mood][tense]['p'][person]['i'][n] = t_ending + '<b>' + red_ending + '</b>'
                else:
                    t_ending = t_endings
                    if t_ending == None:
                        continue
                    t_ending, red_ending = check_red_end(t_ending, red_endings)
                    if red_ending != None:
                        t.new_data[mood][tense]['p'][person]['i'] = t_ending + '<b>' + red_ending + '</b>'
        t.save()



class Command(BaseCommand):
    def handle(self, *args, **options):
        # fix_null()
        # print_wrong_ends()
        # color = colorama.init()
        # print_list_imperative()
        table = import_table()
        make_blue(table)
        make_red()
