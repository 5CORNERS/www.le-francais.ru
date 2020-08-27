import json
import os
import re
from pathlib import Path

import dictdiffer
from bs4 import BeautifulSoup, Tag
from django.core.management import BaseCommand

from conjugation.consts import VOICE_ACTIVE, GENDER_MASCULINE, VOICE_PASSIVE, VOICE_REFLEXIVE, GENDER_FEMININE
from conjugation.management.commands.parse_le_conjugueur import MOODS_TO_KEYS, TENSES_TO_KEYS, FORMULAS_SWITCHES, parse_le_conjugueur_url
from conjugation.models import Verb
from conjugation.table import Table, get_table


def get_conjugueur_url(verb: Verb, negative=False, question=False, voice=VOICE_ACTIVE, pronoun=False,
                       gender=GENDER_MASCULINE):
    parts = []
    if gender == GENDER_FEMININE:
        parts.append('feminin')
    if negative:
        parts.append('negation')
    if question:
        parts.append('question')
    if voice == VOICE_REFLEXIVE:
        if pronoun:
            parts.append('pronominal-en')
        else:
            parts.append('pronominal')
    elif voice == VOICE_PASSIVE:
        parts.append('voix-passive')
    if parts:
        url = f'https://leconjugueur.lefigaro.fr/conjugaison/verbe/{verb.infinitive_no_accents}_{"-".join(parts)}.html'
    else:
        url = f'https://leconjugueur.lefigaro.fr/conjugaison/verbe/{verb.infinitive_no_accents}.html'
    return url


def key_to_switches(key):
    switches = dict(
        negative=False, question=False, voice=VOICE_ACTIVE, pronoun=False, gender=GENDER_MASCULINE
    )
    if 'QUESTION' in key:
        switches['question'] = True
    if 'NEGATIVE' in key:
        switches['negative'] = True
    if 'S-EN' in key:
        switches['voice'], switches['pronoun'] = VOICE_REFLEXIVE, True
    elif 'REFLEXIVE' in key:
        switches['voice'] = VOICE_REFLEXIVE
    elif 'PASSIVE' in key:
        switches['voice'] = VOICE_PASSIVE

    return switches


def get_kwargs(verb:Verb):
    combinations = []

    for key in FORMULAS_SWITCHES.values():
        combination = key_to_switches(key)
        if not verb.can_reflexive and combination['voice'] == VOICE_REFLEXIVE:
            continue
        elif not verb.can_passive and combination['voice'] == VOICE_PASSIVE:
            continue
        elif not verb.can_feminin and combination['gender'] == GENDER_FEMININE:
            continue
        elif not verb.can_be_pronoun and combination['pronoun']:
            continue
        elif not verb.can_be_active and combination['voice'] == VOICE_ACTIVE:
            continue
        combinations.append((combination, key))

    return combinations


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--verb', dest='verbs', action='append', type=str)
        parser.add_argument('--count', type=int)
        parser.add_argument('--no-cache', dest='no_cache', action='store_true')

    def handle(self, *args, **options):
        result_file =  open('conjugation/data/compare/result.txt', 'w', encoding='utf-8')
        same_file = open('conjugation/data/compare/same.txt', 'w', encoding='utf-8')
        verbs = Verb.objects.prefetch_related('template').order_by('-count')
        result = {}
        full_identity = []
        if options['verbs']:
            verbs = verbs.filter(infinitive__in=options['verbs'])
        else:
            verbs = verbs.all()
        if options['count']:
            verbs = verbs[:options['count']]
        l = len(verbs)
        for n, verb in enumerate(verbs,1):
            same = True
            print(f'{n}/{l}')
            result[f'{verb.infinitive}\t{verb.template.name}'] = {}
            if verb.conjugated_with_avoir and verb.conjugated_with_etre:
                etre_or_avoir = 'both'
            elif verb.conjugated_with_etre:
                ...
            else:
                etre_or_avoir = 'avoir'
            for combination, key in get_kwargs(verb):
                p = Path(f'conjugation/data/compare/temp/{verb.infinitive}_{key}.json')
                if not p.exists() or options['no_cache']:
                    conjugueur_conjugations, identity = parse_le_conjugueur_url(get_conjugueur_url(verb, **combination), verb, check_identity=True)
                    if not identity:
                        print(f'IDENTITY FAILED')
                        continue
                    print(f'Comparing with https://www.le-francais.ru{verb.get_url(**combination)}')
                    print('...conjugating')
                    verb_conjugations = get_table(verb, **combination).to_dict()
                    print('...comparing')
                    differences = list(dictdiffer.diff(conjugueur_conjugations, verb_conjugations))
                    temp_file = p.open('w', encoding='utf-8')
                    print(f'...writing to {temp_file.name}')
                    json.dump(differences, temp_file)
                    temp_file.close()
                else:
                    temp_file = p.open('r', encoding='utf-8')
                    differences = json.load(temp_file)
                    temp_file.close()
                if differences:
                    result[f'{verb.infinitive}\t{verb.template.name}'][key] = []
                    for diff in differences:
                        if diff[0] == 'remove' and diff[1] == 'conditional' and diff[2][0][0] == 'past-second':
                            # for some reason we do not have 'past-second'
                            continue
                        same = False
                        result[f'{verb.infinitive}\t{verb.template.name}'][key].append(diff)
            if same:
                full_identity.append(f'{verb.infinitive}\t{verb.template.name}')
        for verb, combinations in result.items():
            for switch, diffs in combinations.items():
                if diffs:
                    print(f'{verb}\t{switch}\t', file=result_file)
                    for diff in diffs:
                        print(diff, file=result_file)
        for line in full_identity:
            print(line, file=same_file)
