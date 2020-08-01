import re

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
        combinations.append(combination)

    return combinations


class Command(BaseCommand):
    def handle(self, *args, **options):
        for verb in Verb.objects.prefetch_related('template').all().order_by('-count'):
            for combination in get_kwargs(verb):
                conjugueur_conjugations = parse_le_conjugueur_url(get_conjugueur_url(verb, **combination), verb)
                print(f'Comparing with https://www.le-francais.ru{verb.get_url(**combination)}')
                verb_conjugations = get_table(verb, **combination).to_dict()
                differences = dictdiffer.diff(conjugueur_conjugations, verb_conjugations)
                for diff in list(differences):
                    if diff[0] == 'remove' and diff[1] == 'conditional' and diff[2][0][0] == 'past-second':
                        # for some reason we do not have 'past-second'
                        continue
                    elif diff[0] == 'change' and diff[1] == ['participle', 'past', 2]:
                        # participle-past are totally different
                        continue
                    elif diff[0] == 'remove' and diff[1] == 'participle.past':
                        # participle-past are totally different
                        continue
                    print(f'{verb.infinitive}\t{diff}')

