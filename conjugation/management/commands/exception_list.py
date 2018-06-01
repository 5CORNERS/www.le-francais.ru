import re

from django.core.management.base import BaseCommand
from pandas import read_csv
from unidecode import unidecode

from conjugation.models import DeffectivePattern, Verb as V, ReflexiveVerb as RV, Regle


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
    if param==True or param=='1' or param==1:
        return True
    elif isinstance(param, str):
        if param.lower()=='true':
            return True
        else:
            return False
    else:
        return False


def fill_other_parametres():
    error_verbs = []
    file_path = "conjugation/data/Full verb list.csv"
    table = read_csv(open(file_path,encoding='utf-8'))
    dict = table.to_dict()
    print(0)
    for i in range(len(dict['VERB'])):
        if i == 0:
            continue
        try:
            v, created = V.objects.get_or_create(infinitive=dict['VERB'][i])
        except:
            error_verbs.append(dict["VERB"][i])
            continue
        print(dict["VERB"][i])
        s_en = return_true_false(dict["S'EN"][i])
        can_passive = return_true_false(dict["CAN BE PASSIVE"][i])
        can_feminin = return_true_false(dict["CAN BE FEMININ"][i])
        reflexive_only = return_true_false(dict["PRONOMINAL ONLY"][i])
        is_impersonal = return_true_false(dict["IMPERSONNEL"][i])
        book = return_true_false(dict["книжный"][i])
        is_rare = return_true_false(dict["редкоупотребимый"][i])
        is_archaique = return_true_false(dict["устаревший"][i])
        is_slang = return_true_false(dict["слэнг"][i])
        group_no = dict["GROUP No"][i]
        group_str = str(dict["GROUP No"][i])

        regle_id = dict["Règle IDX"][i]
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
        is_defective = return_true_false(dict["DEFECTIVE"][i])

        pp_invariable = return_true_false(dict["PP iNVARIABLE"][i])

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
        # v.group_no = group_no
        v.group_str = group_str
        v.regle = Regle.objects.get(id=regle_id)
        v.pp_invariable = pp_invariable

        if created:
            v.infinitive_no_accents = v.get_infinitive_no_accents()
            if v.can_reflexive or v.reflexive_only:
                reflexive_infinitive = "se " + v.infinitive if v.infnitive_first_letter_is_vowel() else "s'" + v.infinitive
                rv, created = RV.objects.get_or_create(infinitive=reflexive_infinitive, verb=v)
                rv.create_no_accents()
                rv.save()
        v.save()
    print("This verb cause error:")
    for error_verb in error_verbs:
        print(error_verb)


def fill_regles():
    file_path = 'conjugation/data/Règles IDX.csv'
    table = read_csv(open(file_path,encoding='utf-8'))
    dict = table.to_dict()

    for i in range(len(dict['REGLE'])):
        print(i)
        regle, created = Regle.objects.get_or_create(id=dict['ID'][i])
        if created:
            regle.text_fr = dict["REGLE"][i]
            regle.save()


def translate_regles():
    file_path = 'conjugation/data/regle_translations.csv'
    table = read_csv(open(file_path, encoding='utf-8'))
    dict = table.to_dict()

    for i in range(len(dict['IDX'])):
        print(i)
        regle, created = Regle.objects.get_or_create(id=dict['IDX'][i])
        regle.text_rus = '<p>' + re.sub('\n\n', '</p><p>', dict['TRANSLATION'][i]) + '</p>'
        regle.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # fill_deffectives()
        # fill_regles()
        # translate_regles()
        fill_other_parametres()
