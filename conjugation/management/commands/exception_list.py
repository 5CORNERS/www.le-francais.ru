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


def return_true_false(param):
    if param==True or param==1:
        return True
    elif isinstance(param, str):
        if param.lower()=='true':
            return True
        else:
            return False
    else:
        return False


def fill_other_parametres():
    file_path = "conjugation/data/Full verb list.csv"
    table = read_csv(open(file_path,encoding='utf-8'))
    dict = table.to_dict()
    print(0)
    for i in range(len(dict['VERB'])):
        if i == 0:
            continue
        print(dict["VERB"][i], end='')
        try:
            v = V.objects.get(infinitive=dict['VERB'][i])
        except:
            print('\t'+"can't find this verb")
        print("\tfounded")
        s_en = return_true_false(dict["S'EN"][i])
        can_passive = return_true_false(dict["CAN BE PASSIVE"][i])
        can_feminin = return_true_false(dict["CAN BE FEMININ"][i])
        reflexive_only = return_true_false(dict["PRONOMINAL ONLY"][i])
        can_reflexive = return_true_false(dict["CAN BE PRONOMINAL"][i])
        is_second_form = return_true_false(dict["HAVE 2 FORMS OF CONJOUGATION"][i])

        is_frequent = return_true_false(dict["Fréquent"][i])
        is_transitive = return_true_false(dict["Transitif"][i])
        is_intransitive = return_true_false(dict["Intransitif"][i])
        is_pronominal = return_true_false(dict["Intransitif"][i])
        aspirate_h = return_true_false(dict["*"][i])
        belgium = return_true_false(dict["BE"][i])
        africa = return_true_false(dict["Afrique"][i])
        conjugated_with_avoir = return_true_false(dict["AVOIR"][i])
        conjugated_with_etre = return_true_false(dict["ÊTRE"][i])
        is_defective = return_true_false(dict["DEFECTIVE"])
        is_impersonal = return_true_false(dict["IMPERSONNEL"])
        book = return_true_false(dict["книжный"][i])
        is_rare = return_true_false(dict["редкоупотребимый"])
        is_archaique = return_true_false(dict["устаревший"])
        is_slang = return_true_false(dict["слэнг"][i])
        group_no = dict["GROUP No"]

        regle_id = dict["Règle IDX"]

        v.s_en = s_en
        v.can_passive = can_passive
        v.can_feminin = can_feminin
        v.reflexive_only = reflexive_only
        v.can_reflexive = can_reflexive
        v.is_second_form = is_second_form
        v.is_frequent = is_frequent
        v.is_transitive = is_transitive
        v.is_intransitive = is_intransitive
        v.is_pronominal = is_pronominal
        v.aspirate_h = aspirate_h
        v.belgium = belgium
        v.africa = africa
        v.conjugated_with_avoir = conjugated_with_avoir
        v.conjugated_with_etre = conjugated_with_etre
        v.is_defective = is_defective
        v.is_impersonal = is_impersonal
        v.book = book
        v.is_rare = is_rare
        v.is_archaique = is_archaique
        v.is_slang = is_slang
        v.group_no = group_no
        v.regle_id = regle_id

        v.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # fill_deffectives()
        fill_other_parametres()