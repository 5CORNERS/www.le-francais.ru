import re

from django.core.management.base import BaseCommand
from pandas import read_csv
from unidecode import unidecode

from conjugation.models import DeffectivePattern, Verb as V, ReflexiveVerb as RV


def fill_deffectives():
    file = open('conjugation/data/Defectives.csv', 'r', encoding='utf-8')
    deffective_table = read_csv(file)
    deffective_dict = deffective_table.to_dict()
    verb_does_not_exist = []
    for index in range(len(deffective_dict['VERB'])):
        verb = deffective_dict['VERB'][index]
        deffective_list = deffective_dict['LIST'][index].strip("[]'").split("','")

        verb_deffective_dict = dict(
            indicative_compose_past=False,
            indicative_anterieur_past=False,
            indicative_pluperfect=False,
            indicative_anterieur_future=False,
            subjunctive_past=False,
            subjunctive_pluperfect=False,
            conditional_past_first=False,
            conditional_past_second=False,
            imperative_past=False,
            infinitive_past=False,
            gerund_past=False,
        )
        for mood_tense in deffective_list:
            mood_tense = re.sub('-', '_', mood_tense)
            mood_tense = unidecode(mood_tense)
            verb_deffective_dict[mood_tense] = True

        indicative_compose_past = True if verb_deffective_dict['indicative_compose_past'] else False
        indicative_anterieur_past = True if verb_deffective_dict['indicative_anterieur_past'] else False
        indicative_pluperfect = True if verb_deffective_dict['indicative_pluperfect'] else False
        indicative_anterieur_future = True if verb_deffective_dict['indicative_anterieur_future'] else False
        subjunctive_past = True if verb_deffective_dict['subjunctive_past'] else False
        subjunctive_pluperfect = True if verb_deffective_dict['subjunctive_pluperfect'] else False
        conditional_past_first = True if verb_deffective_dict['conditional_past_first'] else False
        conditional_past_second = True if verb_deffective_dict['conditional_past_second'] else False
        imperative_past = True if verb_deffective_dict['imperative_past'] else False
        infinitive_past = True if verb_deffective_dict['infinitive_past'] else False
        gerund_past = True if verb_deffective_dict['gerund_past'] else False

        deffective, create = DeffectivePattern.objects.get_or_create(indicative_compose_past=indicative_compose_past,
                                                                     indicative_anterieur_past=indicative_anterieur_past,
                                                                     indicative_pluperfect=indicative_pluperfect,
                                                                     indicative_anterieur_future=indicative_anterieur_future,
                                                                     subjunctive_past=subjunctive_past,
                                                                     subjunctive_pluperfect=subjunctive_pluperfect,
                                                                     conditional_past_first=conditional_past_first,
                                                                     conditional_past_second=conditional_past_second,
                                                                     imperative_past=imperative_past,
                                                                     infinitive_past=infinitive_past,
                                                                     gerund_past=gerund_past)

        print(verb)
        try:
            v = V.objects.get(infinitive=verb)
        except:
            try:
                v = RV.objects.get(infinitive=verb)
            except:
                verb_does_not_exist.append(verb)
                continue

        v.is_deffective = True
        v.deffective = deffective
        v.save()

    print(verb_does_not_exist)


def fill_other_parametres():
    file_path = "conjugation/data/Full verb list.csv"


class Command(BaseCommand):
    def handle(self, *args, **options):
        # fill_deffectives()
        fill_other_parametres()