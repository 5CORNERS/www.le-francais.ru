from django.http import Http404, JsonResponse
from django.shortcuts import render

from conjugation.models import Verb as V
from .utils import get_conjugations

STRUCTRE = {

}

VERB_PRESENT_1 = 'indicative_present_0'
VERB_PRESENT_2 = 'indicative_present_1'
VERB_PRESENT_3 = 'indicative_present_2'
VERB_PRESENT_4 = 'indicative_present_3'
VERB_PRESENT_5 = 'indicative_present_4'
VERB_PRESENT_6 = 'indicative_present_5'

VERB_IMPERFECT_1 = 'indicative_imperfect_0'
VERB_IMPERFECT_2 = 'indicative_imperfect_1'
VERB_IMPERFECT_3 = 'indicative_imperfect_2'
VERB_IMPERFECT_4 = 'indicative_imperfect_3'
VERB_IMPERFECT_5 = 'indicative_imperfect_4'
VERB_IMPERFECT_6 = 'indicative_imperfect_5'

VERB_FUTURE_1 = 'indicative_future_0'
VERB_FUTURE_2 = 'indicative_future_1'
VERB_FUTURE_3 = 'indicative_future_2'
VERB_FUTURE_4 = 'indicative_future_3'
VERB_FUTURE_5 = 'indicative_future_4'
VERB_FUTURE_6 = 'indicative_future_5'

VERB_SIMPLE_PAST_1 = 'indicative_simple-past_0'
VERB_SIMPLE_PAST_2 = 'indicative_simple-past_1'
VERB_SIMPLE_PAST_3 = 'indicative_simple-past_2'
VERB_SIMPLE_PAST_4 = 'indicative_simple-past_3'
VERB_SIMPLE_PAST_5 = 'indicative_simple-past_4'
VERB_SIMPLE_PAST_6 = 'indicative_simple-past_5'

VERB_SUBJUNCTIVE_PRESENT_1 = 'subjunctive_present_0'
VERB_SUBJUNCTIVE_PRESENT_2 = 'subjunctive_present_1'
VERB_SUBJUNCTIVE_PRESENT_3 = 'subjunctive_present_2'
VERB_SUBJUNCTIVE_PRESENT_4 = 'subjunctive_present_3'
VERB_SUBJUNCTIVE_PRESENT_5 = 'subjunctive_present_4'
VERB_SUBJUNCTIVE_PRESENT_6 = 'subjunctive_present_5'

VERB_SUBJUNCTIVE_IMPERFECT_1 = 'subjunctive_imperfect_0'
VERB_SUBJUNCTIVE_IMPERFECT_2 = 'subjunctive_imperfect_1'
VERB_SUBJUNCTIVE_IMPERFECT_3 = 'subjunctive_imperfect_2'
VERB_SUBJUNCTIVE_IMPERFECT_4 = 'subjunctive_imperfect_3'
VERB_SUBJUNCTIVE_IMPERFECT_5 = 'subjunctive_imperfect_4'
VERB_SUBJUNCTIVE_IMPERFECT_6 = 'subjunctive_imperfect_5'

VERB_CONDITIONAL_PRESENT_1 = 'conditional_present_0'
VERB_CONDITIONAL_PRESENT_2 = 'conditional_present_1'
VERB_CONDITIONAL_PRESENT_3 = 'conditional_present_2'
VERB_CONDITIONAL_PRESENT_4 = 'conditional_present_3'
VERB_CONDITIONAL_PRESENT_5 = 'conditional_present_4'
VERB_CONDITIONAL_PRESENT_6 = 'conditional_present_5'

VERB_IMPERATIVE_PRESENT_II_S = 'imperative_imperative-present_0'
VERB_IMPERATIVE_PRESENT_I_P = 'imperative_imperative-present_1'
VERB_IMPERATIVE_PRESENT_II_P = 'imperative_imperative-present_2'

VERB_PRESENT_PARTICIPLE = 'participle_present-participle_0'

VERB_PAST_PARTICIPLE_S_M = 'participle_past-participle_0'
VERB_PAST_PARTICIPLE_S_F = 'participle_past-participle_1'
VERB_PAST_PARTICIPLE_P_M = 'participle_past-participle_2'
VERB_PAST_PARTICIPLE_P_F = 'participle_past-participle_3'


def get_conjugation(request, verb):
    try:
        v = V.objects.get(infinitive=verb)
    except V.DoesNotExist:
        raise Http404('Verb does not exist')
    return JsonResponse(get_conjugations(v))


def get_parler_table(request):
    v = V.objects.get(infinitive='parler')
    table = Table(v)
    template_name = 'conjugation/templates/table.html'
    return render(request, template_name, {

    })


class Table:
    def __init__(self, v: V):
        self.v = v


class Mood:
    pass


class Tense:
    PERSONS_STRUCTRE = {
        'tense': [
            'person_I_S_M',
            'person_II_S_M',
            'person_III_S_M',
            'person_I_P',
            'person_II_P',
            'person_III_P',
        ],
        'present': [
            'person_I_S_M',
            'person_II_S_M',
            'person_III_S_M',
            'person_I_P',
            'person_II_P',
            'person_III_P',
        ],
        'imperfect': [
            'person_I_S_M',
            'person_II_S_M',
            'person_III_S_M',
            'person_I_P',
            'person_II_P',
            'person_III_P',
        ],
        'future': [
            'person_I_S_M',
            'person_II_S_M',
            'person_III_S_M',
            'person_I_P',
            'person_II_P',
            'person_III_P',
        ],
        'simple-past': [
            'person_I_S_M',
            'person_II_S_M',
            'person_III_S_M',
            'person_I_P',
            'person_II_P',
            'person_III_P'
        ],
        'imperative-present': [
            'person_II_S_M',
            'person_I_P',
            'person_II_P'
        ],
        'present-participle': [
            'person_I_S_M'
        ],
        'past-participle': [
            'person_I_S_M',
            'person_II_S_M',
            'person_III_S_M',
            'person_I_P'],
    }

    def __init__(self, v: V, mood: str, tense: str):
        self.v = v
        self.mood = mood
        self.tense = tense
        self.mood_tense = mood + '_' + tense
        self.persons = self.get_persons_list()

    def get_persons_list(self):
        persons = []
        for person in self.PERSONS_STRUCTRE[self.tense]:
            persons.append(Person(self.v, self.mood, self.tense, person))
        return persons


class Person:
    RED_ENDINGS = {
        'indicative_present': {
            'person_I_S_M': ['e', 's'],
            'person_II_S_M': ['es', 's'],
            'person_III_S_M': ['e', 't', 'd'],
            'person_I_P': ['ons'],
            'person_II_P': ['ez', 'es'],
            'person_III_P': ['ent']
        },
        'indicative_imperfect': {
            'person_I_S_M': ['ais'],
            'person_II_S_M': ['ais'],
            'person_III_S_M': ['ait'],
            'person_I_P': ['ions'],
            'person_II_P': ['iez'],
            'person_III_P': ['aient']
        },
        'indicative_future': {
            'person_I_S_M': ['ai'],
            'person_II_S_M': ['as'],
            'person_III_S_M': ['a'],
            'person_I_P': ['ons'],
            'person_II_P': ['ez'],
            'person_III_P': ['ont']
        },
        'indicative_simple-past': {
            'person_I_S_M': ['ai', 'is', 'us'],
            'person_II_S_M': ['as', 'is', 'us'],
            'person_III_S_M': ['a', 'it', 'ut'],
            'person_I_P': ['âmes', 'imes', 'ûmes'],
            'person_II_P': ['âtes', 'îtes', 'ûtes'],
            'person_III_P': ['aient']
        },
        'conditional_present': {
            'person_I_S_M': ['ais'],
            'person_II_S_M': ['ais'],
            'person_III_S_M': ['ait'],
            'person_I_P': ['ions'],
            'person_II_P': ['ez'],
            'person_III_P': ['aient']
        },
        'subjunctive_present': {
            'person_I_S_M': ['e'],
            'person_II_S_M': ['es'],
            'person_III_S_M': ['e'],
            'person_I_P': ['ions'],
            'person_II_P': ['iez'],
            'person_III_P': ['ent'],
        },
        'subjunctive_imperfect': {
            'person_I_S_M': ['asse', 'isse', 'usse'],
            'person_II_S_M': ['asses', '1sses', 'usses'],
            'person_III_S_M': ['ât', 'ît', 'ût'],
            'person_I_P': ['assions', 'issions', 'ussions'],
            'person_II_P': ['assiez', 'issiez', 'ussiez'],
            'person_III_P': ['assent', 'issent', 'ussent'],
        },
        'imperative_present': {
            'person_II_S_M': ['e', 'is', 's'],
            'person_I_P': ['ons', 'issons'],
            'person_II_P': ['ez', 'es', 'issez'],
        },
        'participle_present-participle': {
            'person_I_S_M': ['ant'],
        },
        'participle_past-participle': {
            'person_I_S_M': ['é', 'i', 'ï', 'it', 'is', 'u', 'û'],
            'person_II_S_M': ['és', 'is', 'ïs', 'it', 'us', 'ûs'],
            'person_III_S_M': ['ée', 'ise', 'ïse', 'ite', 'ue', 'ûe'],
            'person_I_P': ['ées', 'ises', 'ïses', 'ites', 'ue', 'ûe'],
        }
    }
    FORMULAS = {
        'indicative': {
            'present': {
                1: {
                    'person_I_S_M': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1),
                    'person_I_S_F': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1),
                    'person_II_S_M': ("tu " + VERB_PRESENT_2),
                    'person_II_S_F': ("tu " + VERB_PRESENT_2),
                    'person_III_S_M': ("il " + VERB_PRESENT_3),
                    'person_III_S_F': ("elle " + VERB_PRESENT_3),
                    'person_I_P_M': ("nous " + VERB_PRESENT_4),
                    'person_I_P_F': ("nous " + VERB_PRESENT_4),
                    'person_II_P_M': ("vous " + VERB_PRESENT_5),
                    'person_II_P_F': ("vous " + VERB_PRESENT_5),
                    'person_III_P_M': ("ils " + VERB_PRESENT_6),
                    'persin_III_P_F': ("elles " + VERB_PRESENT_6),
                },
                2: {
                    'person_I_S_M': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1),
                    'person_I_S_F': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1),
                    'person_II_S_M': ("tu " + VERB_PRESENT_2),
                    'person_II_S_F': ("tu " + VERB_PRESENT_2),
                    'person_III_S_M': ("il " + VERB_PRESENT_3),
                    'person_III_S_F': ("elle " + VERB_PRESENT_3),
                    'person_I_P_M': ("nous " + VERB_PRESENT_4),
                    'person_I_P_F': ("nous " + VERB_PRESENT_4),
                    'person_II_P_M': ("vous " + VERB_PRESENT_5),
                    'person_II_P_F': ("vous " + VERB_PRESENT_5),
                    'person_III_P_M': ("ils " + VERB_PRESENT_6),
                    'persin_III_P_F': ("elles " + VERB_PRESENT_6),
                },
            },
            'simple-past': {
                1: {
                    'person_I_S_M': ("je " + VERB_SIMPLE_PAST, "j'" + VERB_SIMPLE_PAST),
                    'person_I_S_F': ("je " + VERB_SIMPLE_PAST, "j'" + VERB_SIMPLE_PAST),
                    'person_II_S_M': ("tu " + VERB_SIMPLE_PAST),
                    'person_II_S_F': ("tu " + VERB_SIMPLE_PAST),
                    'person_III_S_M': ("il " + VERB_SIMPLE_PAST),
                    'person_III_S_F': ("elle " + VERB_SIMPLE_PAST),
                    'person_I_P_M': ("nous " + VERB_SIMPLE_PAST),
                    'person_I_P_F': ("nous " + VERB_SIMPLE_PAST),
                    'person_II_P_M': ("vous " + VERB_SIMPLE_PAST),
                    'person_II_P_F': ("vous " + VERB_SIMPLE_PAST),
                    'person_III_P_M': ("ils " + VERB_SIMPLE_PAST),
                    'persin_III_P_F': ("elles " + VERB_SIMPLE_PAST),
                },
                2: {
                    'person_I_S_M': ("je " + VERB_SIMPLE_PAST, "j'" + VERB_SIMPLE_PAST),
                    'person_I_S_F': ("je " + VERB_SIMPLE_PAST, "j'" + VERB_SIMPLE_PAST),
                    'person_II_S_M': ("tu " + VERB_SIMPLE_PAST),
                    'person_II_S_F': ("tu " + VERB_SIMPLE_PAST),
                    'person_III_S_M': ("il " + VERB_SIMPLE_PAST),
                    'person_III_S_F': ("elle " + VERB_SIMPLE_PAST),
                    'person_I_P_M': ("nous " + VERB_SIMPLE_PAST),
                    'person_I_P_F': ("nous " + VERB_SIMPLE_PAST),
                    'person_II_P_M': ("vous " + VERB_SIMPLE_PAST),
                    'person_II_P_F': ("vous " + VERB_SIMPLE_PAST),
                    'person_III_P_M': ("ils " + VERB_SIMPLE_PAST),
                    'persin_III_P_F': ("elles " + VERB_SIMPLE_PAST),
                }
            },
            'composé-past': {
                1: {
                    'person_I_S_M': ("j'ai " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'ai " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("tu as " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu as " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("il a " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle a " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("nous avons " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("nous avons " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("vous avez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("vous avez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("ils ont " + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("elles ont " + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {

                    'person_I_S_M': ("je suis " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("je suis " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("tu es " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu es " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("il est " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle est " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("nous sommes " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("nous sommes " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("vous êtes " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("vous êtes " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("ils sont " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("elles sont " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
            'antérieur-past': {
                1: {
                    'person_I_S_M': ("j'eus " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'eus " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("tu eus " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu eus " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("il eut" + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle eut" + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("nous eûmes " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("nous eûmes " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("vous eûtes " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("vous eûtes " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("ils eurent" + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("elles eurent" + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {
                    'person_I_S_M': ("je fus " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("je fus " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("tu fus" + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu fus" + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("il fut " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle fut " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("nous fûmes " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("nous fûmes " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("vous fûtes " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("vous fûtes " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("ils furent " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("elles furent " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
            'imperfect': {
                1: {
                    'person_I_S_M': ("je " + VERB_IMPERFECT, "j'" + VERB_IMPERFECT),
                    'person_I_S_F': ("je " + VERB_IMPERFECT, "j'" + VERB_IMPERFECT),
                    'person_II_S_M': ("tu " + VERB_IMPERFECT),
                    'person_II_S_F': ("tu " + VERB_IMPERFECT),
                    'person_III_S_M': ("il " + VERB_IMPERFECT),
                    'person_III_S_F': ("elle " + VERB_IMPERFECT),
                    'person_I_P_M': ("nous " + VERB_IMPERFECT),
                    'person_I_P_F': ("nous " + VERB_IMPERFECT),
                    'person_II_P_M': ("vous " + VERB_IMPERFECT),
                    'person_II_P_F': ("vous " + VERB_IMPERFECT),
                    'person_III_P_M': ("ils " + VERB_IMPERFECT),
                    'persin_III_P_F': ("elles " + VERB_IMPERFECT),
                },
                2: {
                    'person_I_S_M': ("je " + VERB_IMPERFECT, "j'" + VERB_IMPERFECT),
                    'person_I_S_F': ("je " + VERB_IMPERFECT, "j'" + VERB_IMPERFECT),
                    'person_II_S_M': ("tu " + VERB_IMPERFECT),
                    'person_II_S_F': ("tu " + VERB_IMPERFECT),
                    'person_III_S_M': ("il " + VERB_IMPERFECT),
                    'person_III_S_F': ("elle " + VERB_IMPERFECT),
                    'person_I_P_M': ("nous " + VERB_IMPERFECT),
                    'person_I_P_F': ("nous " + VERB_IMPERFECT),
                    'person_II_P_M': ("vous " + VERB_IMPERFECT),
                    'person_II_P_F': ("vous " + VERB_IMPERFECT),
                    'person_III_P_M': ("ils " + VERB_IMPERFECT),
                    'persin_III_P_F': ("elles " + VERB_IMPERFECT),
                },
            },
            'future': {
                1: {
                    'person_I_S_M': ("je " + VERB_FUTURE, "j'" + VERB_FUTURE),
                    'person_I_S_F': ("je " + VERB_FUTURE, "j'" + VERB_FUTURE),
                    'person_II_S_M': ("tu " + VERB_FUTURE),
                    'person_II_S_F': ("tu " + VERB_FUTURE),
                    'person_III_S_M': ("il " + VERB_FUTURE),
                    'person_III_S_F': ("elle " + VERB_FUTURE),
                    'person_I_P_M': ("nous " + VERB_FUTURE),
                    'person_I_P_F': ("nous " + VERB_FUTURE),
                    'person_II_P_M': ("vous " + VERB_FUTURE),
                    'person_II_P_F': ("vous " + VERB_FUTURE),
                    'person_III_P_M': ("ils " + VERB_FUTURE),
                    'persin_III_P_F': ("elles " + VERB_FUTURE),
                },
                2: {
                    'person_I_S_M': ("je " + VERB_FUTURE, "j'" + VERB_FUTURE),
                    'person_I_S_F': ("je " + VERB_FUTURE, "j'" + VERB_FUTURE),
                    'person_II_S_M': ("tu " + VERB_FUTURE),
                    'person_II_S_F': ("tu " + VERB_FUTURE),
                    'person_III_S_M': ("il " + VERB_FUTURE),
                    'person_III_S_F': ("elle " + VERB_FUTURE),
                    'person_I_P_M': ("nous " + VERB_FUTURE),
                    'person_I_P_F': ("nous " + VERB_FUTURE),
                    'person_II_P_M': ("vous " + VERB_FUTURE),
                    'person_II_P_F': ("vous " + VERB_FUTURE),
                    'person_III_P_M': ("ils " + VERB_FUTURE),
                    'persin_III_P_F': ("elles " + VERB_FUTURE),
                }
            },
            'pluperfect': {
                1: {
                    'person_I_S_M': ("j'avais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'avais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("tu avais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu avais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("il avait" + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle avait" + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("nous avions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("nous avions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("vous aviez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("vous aviez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("ils avaient" + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("elles avaient" + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {
                    'person_I_S_M': ("j'étais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'étais " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("tu étais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu étais " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("il était " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle était " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("nous étions " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("nous étions " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("vous étiez " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("vous étiez " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("ils étaient " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("elles étaient " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
            'antérieur-future': {
                1: {
                    'person_I_S_M': ("j'aurai " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'aurai " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("tu auras " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu auras " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("il aura " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle aura " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("nous aurons " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("nous aurons " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("vous aurez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("vous aurez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("ils auront " + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("elles auront " + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {
                    'person_I_S_M': ("je serai " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("je serai " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("tu seras " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu seras " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("il sera " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle sera " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("nous serons " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("nous serons " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("vous serez " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("vous serez " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("ils seront " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("elles seront " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
        },
        'subjunctive': {
            'present': {
                1: {
                    'person_I_S_M': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1),
                    'person_I_S_F': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1),
                    'person_II_S_M': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2),
                    'person_II_S_F': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2),
                    'person_III_S_M': ("il " + VERB_SUBJUNCTIVE_PRESENT_3),
                    'person_III_S_F': ("elle " + VERB_SUBJUNCTIVE_PRESENT_3),
                    'person_I_P_M': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4),
                    'person_I_P_F': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4),
                    'person_II_P_M': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5),
                    'person_II_P_F': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5),
                    'person_III_P_M': ("ils " + VERB_SUBJUNCTIVE_PRESENT_6),
                    'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_PRESENT_6),
                },
                2: {
                    'person_I_S_M': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1),
                    'person_I_S_F': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1),
                    'person_II_S_M': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2),
                    'person_II_S_F': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2),
                    'person_III_S_M': ("il " + VERB_SUBJUNCTIVE_PRESENT_3),
                    'person_III_S_F': ("elle " + VERB_SUBJUNCTIVE_PRESENT_3),
                    'person_I_P_M': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4),
                    'person_I_P_F': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4),
                    'person_II_P_M': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5),
                    'person_II_P_F': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5),
                    'person_III_P_M': ("ils " + VERB_SUBJUNCTIVE_PRESENT_6),
                    'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_PRESENT_6),
                },
            },
            'past': {
                1: {
                    'person_I_S_M': ("que j'aie " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("que j'aie " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("que tu aies " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("que tu aies " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("qu'il ait " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("qu'elle ait " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("que nous ayons " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("que nous ayons " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("que vous ayez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("que vous ayez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("qu'ils aient " + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("qu'elles aient " + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {

                    'person_I_S_M': ("que je sois " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("que je sois " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("que tu sois " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("que tu sois " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("qu'il soit " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("qu'elle soit " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("que nous soyons " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("que nous soyons " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("que vous soyez " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("que vous soyez " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("qu'ils soient " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("qu'elles soient " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
            'imperfect': {
                1: {
                    'person_I_S_M': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1),
                    'person_I_S_F': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1),
                    'person_II_S_M': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2),
                    'person_II_S_F': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2),
                    'person_III_S_M': ("qu'il " + VERB_SUBJUNCTIVE_IMPERFECT_3),
                    'person_III_S_F': ("qu'elle " + VERB_SUBJUNCTIVE_IMPERFECT_3),
                    'person_I_P_M': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4),
                    'person_I_P_F': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4),
                    'person_II_P_M': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5),
                    'person_II_P_F': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5),
                    'person_III_P_M': ("qu'ils " + VERB_SUBJUNCTIVE_IMPERFECT_6),
                    'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_IMPERFECT_6),
                },
                2: {
                    'person_I_S_M': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1),
                    'person_I_S_F': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1),
                    'person_II_S_M': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2),
                    'person_II_S_F': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2),
                    'person_III_S_M': ("qu'il " + VERB_SUBJUNCTIVE_IMPERFECT_3),
                    'person_III_S_F': ("qu'elle " + VERB_SUBJUNCTIVE_IMPERFECT_3),
                    'person_I_P_M': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4),
                    'person_I_P_F': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4),
                    'person_II_P_M': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5),
                    'person_II_P_F': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5),
                    'person_III_P_M': ("qu'ils " + VERB_SUBJUNCTIVE_IMPERFECT_6),
                    'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_IMPERFECT_6),
                },
            },
            'pluperfect': {
                1: {
                    'person_I_S_M': ("que j'eusse " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("que j'eusse " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("que tu eusses " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("que tu eusses " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("qu'il eût " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("qu'elle eût " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("que nous eussions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("que nous eussions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("que vous eussiez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("que vous eussiez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("qu'ils eussent " + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("qu'elles eussent " + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {

                    'person_I_S_M': ("que je fusse " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("que je fusse " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("que tu fusses " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("que tu fusses " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("qu'il fût " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("qu'elle fût " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("que nous fussions " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("que nous fussions " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("que vous fussiez " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("que vous fussiez " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("qu'ils fussent " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("qu'elles fussent " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
        },
        'conditional': {
            'present': {
                1: {
                    'person_I_S_M': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1),
                    'person_I_S_F': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1),
                    'person_II_S_M': ("tu " + VERB_CONDITIONAL_PRESENT_2),
                    'person_II_S_F': ("tu " + VERB_CONDITIONAL_PRESENT_2),
                    'person_III_S_M': ("il " + VERB_CONDITIONAL_PRESENT_3),
                    'person_III_S_F': ("elle " + VERB_CONDITIONAL_PRESENT_3),
                    'person_I_P_M': ("nous " + VERB_CONDITIONAL_PRESENT_4),
                    'person_I_P_F': ("nous " + VERB_CONDITIONAL_PRESENT_4),
                    'person_II_P_M': ("vous " + VERB_CONDITIONAL_PRESENT_5),
                    'person_II_P_F': ("vous " + VERB_CONDITIONAL_PRESENT_5),
                    'person_III_P_M': ("ils " + VERB_CONDITIONAL_PRESENT_6),
                    'persin_III_P_F': ("elles " + VERB_CONDITIONAL_PRESENT_6),
                },
                2: {
                    'person_I_S_M': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1),
                    'person_I_S_F': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1),
                    'person_II_S_M': ("tu " + VERB_CONDITIONAL_PRESENT_2),
                    'person_II_S_F': ("tu " + VERB_CONDITIONAL_PRESENT_2),
                    'person_III_S_M': ("il " + VERB_CONDITIONAL_PRESENT_3),
                    'person_III_S_F': ("elle " + VERB_CONDITIONAL_PRESENT_3),
                    'person_I_P_M': ("nous " + VERB_CONDITIONAL_PRESENT_4),
                    'person_I_P_F': ("nous " + VERB_CONDITIONAL_PRESENT_4),
                    'person_II_P_M': ("vous " + VERB_CONDITIONAL_PRESENT_5),
                    'person_II_P_F': ("vous " + VERB_CONDITIONAL_PRESENT_5),
                    'person_III_P_M': ("ils " + VERB_CONDITIONAL_PRESENT_6),
                    'persin_III_P_F': ("elles " + VERB_CONDITIONAL_PRESENT_6),
                }
            },
            'past-first': {
                1: {
                    'person_I_S_M': ("j'aurais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'aurais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("tu aurais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu aurais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("il aurait " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle aurait " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("nous aurions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("nous aurions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("vous auriez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("vous auriez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("ils auraient " + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("elles auraient " + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {
                    'person_I_S_M': ("je serais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("je serais " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("tu serais " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu serais " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("il serait " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle serait " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("nous serions " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("nous serions " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("vous seriez " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("vous seriez " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("ils seraient " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("elles seraient " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
            'past-second': {
                1: {
                    'person_I_S_M': ("j'eusse " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("j'eusse " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_M': ("tu eusses " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu eusses " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_M': ("il eût " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle eût " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("nous eussions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("nous eussions " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("vous eussiez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_F': ("vous eussiez " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_P_M': ("ils eussent " + VERB_PAST_PARTICIPLE_S_M),
                    'persin_III_P_F': ("elles eussent " + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {

                    'person_I_S_M': ("je fusse " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_S_F': ("je fusse " + VERB_PAST_PARTICIPLE_S_F),
                    'person_II_S_M': ("tu fusses " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("tu fusses " + VERB_PAST_PARTICIPLE_S_F),
                    'person_III_S_M': ("il fût " + VERB_PAST_PARTICIPLE_S_M),
                    'person_III_S_F': ("elle fût " + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("nous fussions " + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("nous fussions " + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("vous fussiez " + VERB_PAST_PARTICIPLE_P_M),
                    'person_II_P_F': ("vous fussiez " + VERB_PAST_PARTICIPLE_P_F),
                    'person_III_P_M': ("ils fussent " + VERB_PAST_PARTICIPLE_P_M),
                    'persin_III_P_F': ("elles fussent " + VERB_PAST_PARTICIPLE_P_F),
                },
            },
        },
        'imperative': {
            'present': {
                1: {
                    'person_II_S_M': (VERB_IMPERATIVE_PRESENT_II_S),
                    'person_II_S_F': (VERB_IMPERATIVE_PRESENT_II_S),
                    'person_I_P_M': (VERB_IMPERATIVE_PRESENT_I_P),
                    'person_I_P_F': (VERB_IMPERATIVE_PRESENT_I_P),
                    'person_II_P_M': (VERB_IMPERATIVE_PRESENT_II_P),
                    'persin_II_P_F': (VERB_IMPERATIVE_PRESENT_II_P),
                },
                2: {
                    'person_II_S_M': (VERB_IMPERATIVE_PRESENT_II_S),
                    'person_II_S_F': (VERB_IMPERATIVE_PRESENT_II_S),
                    'person_I_P_M': (VERB_IMPERATIVE_PRESENT_I_P),
                    'person_I_P_F': (VERB_IMPERATIVE_PRESENT_I_P),
                    'person_II_P_M': (VERB_IMPERATIVE_PRESENT_II_P),
                    'persin_II_P_F': (VERB_IMPERATIVE_PRESENT_II_P),
                },
            },
            'past': {
                1: {
                    'person_II_S_M': ("aie " + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("aie " + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_M': ("ayons" + VERB_PAST_PARTICIPLE_S_M),
                    'person_I_P_F': ("ayons" + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_P_M': ("ayez" + VERB_PAST_PARTICIPLE_S_M),
                    'persin_II_P_F': ("ayez" + VERB_PAST_PARTICIPLE_S_M),
                },
                2: {
                    'person_II_S_M': ("sois" + VERB_PAST_PARTICIPLE_S_M),
                    'person_II_S_F': ("sois" + VERB_PAST_PARTICIPLE_S_F),
                    'person_I_P_M': ("souons" + VERB_PAST_PARTICIPLE_P_M),
                    'person_I_P_F': ("souons" + VERB_PAST_PARTICIPLE_P_F),
                    'person_II_P_M': ("soyez" + VERB_PAST_PARTICIPLE_P_M),
                    'persin_II_P_F': ("soyez" + VERB_PAST_PARTICIPLE_P_F),
                },
            },
        },
        'participle': {
            'present': {
                '': (VERB_PRESENT_PARTICIPLE)  # TODO person name?
            },
            'past': {
                1: {
                    'S_M': (VERB_PAST_PARTICIPLE_S_M),
                    'S_F': (VERB_PAST_PARTICIPLE_S_F),
                    'P_M': (VERB_PAST_PARTICIPLE_P_M),
                    'P_F': (VERB_PAST_PARTICIPLE_P_F),
                    'M': ('ayant ' + VERB_PAST_PARTICIPLE_S_M), # TODO person name?
                    'F': ('ayant ' + VERB_PAST_PARTICIPLE_S_F) # TODO person name?
                },
                2: {
                    'S_M': (VERB_PAST_PARTICIPLE_S_M),
                    'S_F': (VERB_PAST_PARTICIPLE_S_F),
                    'P_M': (VERB_PAST_PARTICIPLE_P_M),
                    'P_F': (VERB_PAST_PARTICIPLE_P_F),
                    'M': ('étant ' + VERB_PAST_PARTICIPLE_S_M), # TODO person name?
                    'F': ('étant ' + VERB_PAST_PARTICIPLE_S_F) # TODO person name?
                }
            }
        }

    def __init__(self, v: V, mood: str, tense: str, person: str):
        self.v = v
        self.verb = v.infinitive
        self.part_1, self.part_2 = self.get_ending(self.template_endings())
        self.mood_tense = mood + '_' + tense
        self.person = person

    def get_ending(self, v1, v2):
        try:
            r_ends = self.RED_ENDINGS[self.mood_tense][self.person]
            for r_end in r_ends:
                if self.verb.endswith(r_end):
                    new_verb_main = self.verb.rstrip(r_end)
                    new_verb_ending = r_end
                    return new_verb_main, new_verb_ending
        except:
            return v1, v2

    def template_endings(self):
        v2 = self.v.template.name.split(':')[1]
        v1 = self.verb.rstrip(v2)
        return v1, v2

    def part_0(self):
