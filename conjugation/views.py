from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from unidecode import unidecode

from conjugation.models import Verb as V, Template as T
from .utils import get_conjugations

STRUCTRE = {

}

VERB_INFINITIVE = '+infinitive_infinitive-present_0+'

VERB_PRESENT_1 = '+indicative_present_0+'
VERB_PRESENT_2 = '+indicative_present_1+'
VERB_PRESENT_3 = '+indicative_present_2+'
VERB_PRESENT_4 = '+indicative_present_3+'
VERB_PRESENT_5 = '+indicative_present_4+'
VERB_PRESENT_6 = '+indicative_present_5+'

VERB_IMPERFECT_1 = '+indicative_imperfect_0+'
VERB_IMPERFECT_2 = '+indicative_imperfect_1+'
VERB_IMPERFECT_3 = '+indicative_imperfect_2+'
VERB_IMPERFECT_4 = '+indicative_imperfect_3+'
VERB_IMPERFECT_5 = '+indicative_imperfect_4+'
VERB_IMPERFECT_6 = '+indicative_imperfect_5+'

VERB_FUTURE_1 = '+indicative_future_0+'
VERB_FUTURE_2 = '+indicative_future_1+'
VERB_FUTURE_3 = '+indicative_future_2+'
VERB_FUTURE_4 = '+indicative_future_3+'
VERB_FUTURE_5 = '+indicative_future_4+'
VERB_FUTURE_6 = '+indicative_future_5+'

VERB_SIMPLE_PAST_1 = '+indicative_simple-past_0+'
VERB_SIMPLE_PAST_2 = '+indicative_simple-past_1+'
VERB_SIMPLE_PAST_3 = '+indicative_simple-past_2+'
VERB_SIMPLE_PAST_4 = '+indicative_simple-past_3+'
VERB_SIMPLE_PAST_5 = '+indicative_simple-past_4+'
VERB_SIMPLE_PAST_6 = '+indicative_simple-past_5+'

VERB_SUBJUNCTIVE_PRESENT_1 = '+subjunctive_present_0+'
VERB_SUBJUNCTIVE_PRESENT_2 = '+subjunctive_present_1+'
VERB_SUBJUNCTIVE_PRESENT_3 = '+subjunctive_present_2+'
VERB_SUBJUNCTIVE_PRESENT_4 = '+subjunctive_present_3+'
VERB_SUBJUNCTIVE_PRESENT_5 = '+subjunctive_present_4+'
VERB_SUBJUNCTIVE_PRESENT_6 = '+subjunctive_present_5+'

VERB_SUBJUNCTIVE_IMPERFECT_1 = '+subjunctive_imperfect_0+'
VERB_SUBJUNCTIVE_IMPERFECT_2 = '+subjunctive_imperfect_1+'
VERB_SUBJUNCTIVE_IMPERFECT_3 = '+subjunctive_imperfect_2+'
VERB_SUBJUNCTIVE_IMPERFECT_4 = '+subjunctive_imperfect_3+'
VERB_SUBJUNCTIVE_IMPERFECT_5 = '+subjunctive_imperfect_4+'
VERB_SUBJUNCTIVE_IMPERFECT_6 = '+subjunctive_imperfect_5+'

VERB_CONDITIONAL_PRESENT_1 = '+conditional_present_0+'
VERB_CONDITIONAL_PRESENT_2 = '+conditional_present_1+'
VERB_CONDITIONAL_PRESENT_3 = '+conditional_present_2+'
VERB_CONDITIONAL_PRESENT_4 = '+conditional_present_3+'
VERB_CONDITIONAL_PRESENT_5 = '+conditional_present_4+'
VERB_CONDITIONAL_PRESENT_6 = '+conditional_present_5+'

VERB_IMPERATIVE_PRESENT_II_S = '+imperative_imperative-present_0+'
VERB_IMPERATIVE_PRESENT_I_P = '+imperative_imperative-present_1+'
VERB_IMPERATIVE_PRESENT_II_P = '+imperative_imperative-present_2+'

VERB_PRESENT_PARTICIPLE = '+participle_present-participle_0+'

VERB_PAST_PARTICIPLE_S_M = '+participle_past-participle_0+'
VERB_PAST_PARTICIPLE_S_F = '+participle_past-participle_2+'
VERB_PAST_PARTICIPLE_P_M = '+participle_past-participle_1+'
VERB_PAST_PARTICIPLE_P_F = '+participle_past-participle_3+'

FORMULAS = {

    'indicative': {
        'present': {
            1: {
                'person_I_S_M': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1,),
                'person_I_S_F': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1,),
                'person_II_S_M': ("tu " + VERB_PRESENT_2,),
                'person_II_S_F': ("tu " + VERB_PRESENT_2,),
                'person_III_S_M': ("il " + VERB_PRESENT_3,),
                'person_III_S_F': ("elle " + VERB_PRESENT_3,),
                'person_I_P_M': ("nous " + VERB_PRESENT_4,),
                'person_I_P_F': ("nous " + VERB_PRESENT_4,),
                'person_II_P_M': ("vous " + VERB_PRESENT_5,),
                'person_II_P_F': ("vous " + VERB_PRESENT_5,),
                'person_III_P_M': ("ils " + VERB_PRESENT_6,),
                'persin_III_P_F': ("elles " + VERB_PRESENT_6,),
            },
            2: {
                'person_I_S_M': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1,),
                'person_I_S_F': ("je " + VERB_PRESENT_1, "j'" + VERB_PRESENT_1,),
                'person_II_S_M': ("tu " + VERB_PRESENT_2,),
                'person_II_S_F': ("tu " + VERB_PRESENT_2,),
                'person_III_S_M': ("il " + VERB_PRESENT_3,),
                'person_III_S_F': ("elle " + VERB_PRESENT_3,),
                'person_I_P_M': ("nous " + VERB_PRESENT_4,),
                'person_I_P_F': ("nous " + VERB_PRESENT_4,),
                'person_II_P_M': ("vous " + VERB_PRESENT_5,),
                'person_II_P_F': ("vous " + VERB_PRESENT_5,),
                'person_III_P_M': ("ils " + VERB_PRESENT_6,),
                'persin_III_P_F': ("elles " + VERB_PRESENT_6,),
            },
        },
        'simple-past': {
            1: {
                'person_I_S_M': ("je " + VERB_SIMPLE_PAST_1, "j'" + VERB_SIMPLE_PAST_1,),
                'person_I_S_F': ("je " + VERB_SIMPLE_PAST_1, "j'" + VERB_SIMPLE_PAST_1,),
                'person_II_S_M': ("tu " + VERB_SIMPLE_PAST_2,),
                'person_II_S_F': ("tu " + VERB_SIMPLE_PAST_2,),
                'person_III_S_M': ("il " + VERB_SIMPLE_PAST_3,),
                'person_III_S_F': ("elle " + VERB_SIMPLE_PAST_3,),
                'person_I_P_M': ("nous " + VERB_SIMPLE_PAST_4,),
                'person_I_P_F': ("nous " + VERB_SIMPLE_PAST_4,),
                'person_II_P_M': ("vous " + VERB_SIMPLE_PAST_5,),
                'person_II_P_F': ("vous " + VERB_SIMPLE_PAST_5,),
                'person_III_P_M': ("ils " + VERB_SIMPLE_PAST_6,),
                'persin_III_P_F': ("elles " + VERB_SIMPLE_PAST_6,),
            },
            2: {
                'person_I_S_M': ("je " + VERB_SIMPLE_PAST_1, "j'" + VERB_SIMPLE_PAST_1,),
                'person_I_S_F': ("je " + VERB_SIMPLE_PAST_1, "j'" + VERB_SIMPLE_PAST_1,),
                'person_II_S_M': ("tu " + VERB_SIMPLE_PAST_2,),
                'person_II_S_F': ("tu " + VERB_SIMPLE_PAST_2,),
                'person_III_S_M': ("il " + VERB_SIMPLE_PAST_3,),
                'person_III_S_F': ("elle " + VERB_SIMPLE_PAST_3,),
                'person_I_P_M': ("nous " + VERB_SIMPLE_PAST_4,),
                'person_I_P_F': ("nous " + VERB_SIMPLE_PAST_4,),
                'person_II_P_M': ("vous " + VERB_SIMPLE_PAST_5,),
                'person_II_P_F': ("vous " + VERB_SIMPLE_PAST_5,),
                'person_III_P_M': ("ils " + VERB_SIMPLE_PAST_6,),
                'persin_III_P_F': ("elles " + VERB_SIMPLE_PAST_6,),
            }
        },
        'composé-past': {
            1: {
                'person_I_S_M': ("j'ai " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'ai " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("tu as " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu as " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("il a " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle a " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("nous avons " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("nous avons " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("vous avez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("vous avez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("ils ont " + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("elles ont " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {

                'person_I_S_M': ("je suis " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("je suis " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("tu es " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu es " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("il est " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle est " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("nous sommes " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("nous sommes " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("vous êtes " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("vous êtes " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("ils sont " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("elles sont " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
        'antérieur-past': {
            1: {
                'person_I_S_M': ("j'eus " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'eus " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("tu eus " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu eus " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("il eut" + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle eut" + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("nous eûmes " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("nous eûmes " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("vous eûtes " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("vous eûtes " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("ils eurent" + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("elles eurent" + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {
                'person_I_S_M': ("je fus " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("je fus " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("tu fus" + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu fus" + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("il fut " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle fut " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("nous fûmes " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("nous fûmes " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("vous fûtes " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("vous fûtes " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("ils furent " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("elles furent " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
        'imperfect': {
            1: {
                'person_I_S_M': ("je " + VERB_IMPERFECT_1, "j'" + VERB_IMPERFECT_1,),
                'person_I_S_F': ("je " + VERB_IMPERFECT_1, "j'" + VERB_IMPERFECT_1,),
                'person_II_S_M': ("tu " + VERB_IMPERFECT_2,),
                'person_II_S_F': ("tu " + VERB_IMPERFECT_2,),
                'person_III_S_M': ("il " + VERB_IMPERFECT_3,),
                'person_III_S_F': ("elle " + VERB_IMPERFECT_3,),
                'person_I_P_M': ("nous " + VERB_IMPERFECT_4,),
                'person_I_P_F': ("nous " + VERB_IMPERFECT_4,),
                'person_II_P_M': ("vous " + VERB_IMPERFECT_5,),
                'person_II_P_F': ("vous " + VERB_IMPERFECT_5,),
                'person_III_P_M': ("ils " + VERB_IMPERFECT_6,),
                'persin_III_P_F': ("elles " + VERB_IMPERFECT_6,),
            },
            2: {
                'person_I_S_M': ("je " + VERB_IMPERFECT_1, "j'" + VERB_IMPERFECT_1,),
                'person_I_S_F': ("je " + VERB_IMPERFECT_1, "j'" + VERB_IMPERFECT_1,),
                'person_II_S_M': ("tu " + VERB_IMPERFECT_2,),
                'person_II_S_F': ("tu " + VERB_IMPERFECT_2,),
                'person_III_S_M': ("il " + VERB_IMPERFECT_3,),
                'person_III_S_F': ("elle " + VERB_IMPERFECT_3,),
                'person_I_P_M': ("nous " + VERB_IMPERFECT_4,),
                'person_I_P_F': ("nous " + VERB_IMPERFECT_4,),
                'person_II_P_M': ("vous " + VERB_IMPERFECT_5,),
                'person_II_P_F': ("vous " + VERB_IMPERFECT_5,),
                'person_III_P_M': ("ils " + VERB_IMPERFECT_6,),
                'persin_III_P_F': ("elles " + VERB_IMPERFECT_6,),
            },
        },
        'future': {
            1: {
                'person_I_S_M': ("je " + VERB_FUTURE_1, "j'" + VERB_FUTURE_1,),
                'person_I_S_F': ("je " + VERB_FUTURE_1, "j'" + VERB_FUTURE_1,),
                'person_II_S_M': ("tu " + VERB_FUTURE_2,),
                'person_II_S_F': ("tu " + VERB_FUTURE_2,),
                'person_III_S_M': ("il " + VERB_FUTURE_3,),
                'person_III_S_F': ("elle " + VERB_FUTURE_3,),
                'person_I_P_M': ("nous " + VERB_FUTURE_4,),
                'person_I_P_F': ("nous " + VERB_FUTURE_4,),
                'person_II_P_M': ("vous " + VERB_FUTURE_5,),
                'person_II_P_F': ("vous " + VERB_FUTURE_5,),
                'person_III_P_M': ("ils " + VERB_FUTURE_6,),
                'persin_III_P_F': ("elles " + VERB_FUTURE_6,),
            },
            2: {
                'person_I_S_M': ("je " + VERB_FUTURE_1, "j'" + VERB_FUTURE_1,),
                'person_I_S_F': ("je " + VERB_FUTURE_1, "j'" + VERB_FUTURE_1,),
                'person_II_S_M': ("tu " + VERB_FUTURE_2,),
                'person_II_S_F': ("tu " + VERB_FUTURE_2,),
                'person_III_S_M': ("il " + VERB_FUTURE_3,),
                'person_III_S_F': ("elle " + VERB_FUTURE_3,),
                'person_I_P_M': ("nous " + VERB_FUTURE_4,),
                'person_I_P_F': ("nous " + VERB_FUTURE_4,),
                'person_II_P_M': ("vous " + VERB_FUTURE_5,),
                'person_II_P_F': ("vous " + VERB_FUTURE_5,),
                'person_III_P_M': ("ils " + VERB_FUTURE_6,),
                'persin_III_P_F': ("elles " + VERB_FUTURE_6,),
            }
        },
        'pluperfect': {
            1: {
                'person_I_S_M': ("j'avais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'avais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("tu avais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu avais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("il avait" + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle avait" + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("nous avions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("nous avions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("vous aviez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("vous aviez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("ils avaient" + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("elles avaient" + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {
                'person_I_S_M': ("j'étais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'étais " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("tu étais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu étais " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("il était " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle était " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("nous étions " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("nous étions " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("vous étiez " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("vous étiez " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("ils étaient " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("elles étaient " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
        'antérieur-future': {
            1: {
                'person_I_S_M': ("j'aurai " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'aurai " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("tu auras " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu auras " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("il aura " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle aura " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("nous aurons " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("nous aurons " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("vous aurez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("vous aurez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("ils auront " + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("elles auront " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {
                'person_I_S_M': ("je serai " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("je serai " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("tu seras " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu seras " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("il sera " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle sera " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("nous serons " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("nous serons " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("vous serez " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("vous serez " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("ils seront " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("elles seront " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
    },
    'subjunctive': {
        'present': {
            1: {
                'person_I_S_M': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1,),
                'person_I_S_F': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1,),
                'person_II_S_M': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2,),
                'person_II_S_F': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2,),
                'person_III_S_M': ("il " + VERB_SUBJUNCTIVE_PRESENT_3,),
                'person_III_S_F': ("elle " + VERB_SUBJUNCTIVE_PRESENT_3,),
                'person_I_P_M': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4,),
                'person_I_P_F': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4,),
                'person_II_P_M': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5,),
                'person_II_P_F': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5,),
                'person_III_P_M': ("ils " + VERB_SUBJUNCTIVE_PRESENT_6,),
                'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_PRESENT_6,),
            },
            2: {
                'person_I_S_M': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1,),
                'person_I_S_F': ("je " + VERB_SUBJUNCTIVE_PRESENT_1, "j'" + VERB_SUBJUNCTIVE_PRESENT_1,),
                'person_II_S_M': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2,),
                'person_II_S_F': ("tu " + VERB_SUBJUNCTIVE_PRESENT_2,),
                'person_III_S_M': ("il " + VERB_SUBJUNCTIVE_PRESENT_3,),
                'person_III_S_F': ("elle " + VERB_SUBJUNCTIVE_PRESENT_3,),
                'person_I_P_M': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4,),
                'person_I_P_F': ("nous " + VERB_SUBJUNCTIVE_PRESENT_4,),
                'person_II_P_M': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5,),
                'person_II_P_F': ("vous " + VERB_SUBJUNCTIVE_PRESENT_5,),
                'person_III_P_M': ("ils " + VERB_SUBJUNCTIVE_PRESENT_6,),
                'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_PRESENT_6,),
            },
        },
        'past': {
            1: {
                'person_I_S_M': ("que j'aie " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("que j'aie " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("que tu aies " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("que tu aies " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("qu'il ait " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("qu'elle ait " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("que nous ayons " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("que nous ayons " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("que vous ayez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("que vous ayez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("qu'ils aient " + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("qu'elles aient " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {

                'person_I_S_M': ("que je sois " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("que je sois " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("que tu sois " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("que tu sois " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("qu'il soit " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("qu'elle soit " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("que nous soyons " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("que nous soyons " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("que vous soyez " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("que vous soyez " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("qu'ils soient " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("qu'elles soient " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
        'imperfect': {
            1: {
                'person_I_S_M': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1,),
                'person_I_S_F': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1,),
                'person_II_S_M': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2,),
                'person_II_S_F': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2,),
                'person_III_S_M': ("qu'il " + VERB_SUBJUNCTIVE_IMPERFECT_3,),
                'person_III_S_F': ("qu'elle " + VERB_SUBJUNCTIVE_IMPERFECT_3,),
                'person_I_P_M': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4,),
                'person_I_P_F': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4,),
                'person_II_P_M': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5,),
                'person_II_P_F': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5,),
                'person_III_P_M': ("qu'ils " + VERB_SUBJUNCTIVE_IMPERFECT_6,),
                'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_IMPERFECT_6,),
            },
            2: {
                'person_I_S_M': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1,),
                'person_I_S_F': ("que je " + VERB_SUBJUNCTIVE_IMPERFECT_1, "que j'" + VERB_SUBJUNCTIVE_IMPERFECT_1,),
                'person_II_S_M': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2,),
                'person_II_S_F': ("que tu " + VERB_SUBJUNCTIVE_IMPERFECT_2,),
                'person_III_S_M': ("qu'il " + VERB_SUBJUNCTIVE_IMPERFECT_3,),
                'person_III_S_F': ("qu'elle " + VERB_SUBJUNCTIVE_IMPERFECT_3,),
                'person_I_P_M': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4,),
                'person_I_P_F': ("que nous " + VERB_SUBJUNCTIVE_IMPERFECT_4,),
                'person_II_P_M': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5,),
                'person_II_P_F': ("que vous " + VERB_SUBJUNCTIVE_IMPERFECT_5,),
                'person_III_P_M': ("qu'ils " + VERB_SUBJUNCTIVE_IMPERFECT_6,),
                'persin_III_P_F': ("elles " + VERB_SUBJUNCTIVE_IMPERFECT_6,),
            },
        },
        'pluperfect': {
            1: {
                'person_I_S_M': ("que j'eusse " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("que j'eusse " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("que tu eusses " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("que tu eusses " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("qu'il eût " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("qu'elle eût " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("que nous eussions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("que nous eussions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("que vous eussiez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("que vous eussiez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("qu'ils eussent " + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("qu'elles eussent " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {

                'person_I_S_M': ("que je fusse " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("que je fusse " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("que tu fusses " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("que tu fusses " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("qu'il fût " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("qu'elle fût " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("que nous fussions " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("que nous fussions " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("que vous fussiez " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("que vous fussiez " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("qu'ils fussent " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("qu'elles fussent " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
    },
    'conditional': {
        'present': {
            1: {
                'person_I_S_M': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1,),
                'person_I_S_F': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1,),
                'person_II_S_M': ("tu " + VERB_CONDITIONAL_PRESENT_2,),
                'person_II_S_F': ("tu " + VERB_CONDITIONAL_PRESENT_2,),
                'person_III_S_M': ("il " + VERB_CONDITIONAL_PRESENT_3,),
                'person_III_S_F': ("elle " + VERB_CONDITIONAL_PRESENT_3,),
                'person_I_P_M': ("nous " + VERB_CONDITIONAL_PRESENT_4,),
                'person_I_P_F': ("nous " + VERB_CONDITIONAL_PRESENT_4,),
                'person_II_P_M': ("vous " + VERB_CONDITIONAL_PRESENT_5,),
                'person_II_P_F': ("vous " + VERB_CONDITIONAL_PRESENT_5,),
                'person_III_P_M': ("ils " + VERB_CONDITIONAL_PRESENT_6,),
                'persin_III_P_F': ("elles " + VERB_CONDITIONAL_PRESENT_6,),
            },
            2: {
                'person_I_S_M': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1,),
                'person_I_S_F': ("je " + VERB_CONDITIONAL_PRESENT_1, "j'" + VERB_CONDITIONAL_PRESENT_1,),
                'person_II_S_M': ("tu " + VERB_CONDITIONAL_PRESENT_2,),
                'person_II_S_F': ("tu " + VERB_CONDITIONAL_PRESENT_2,),
                'person_III_S_M': ("il " + VERB_CONDITIONAL_PRESENT_3,),
                'person_III_S_F': ("elle " + VERB_CONDITIONAL_PRESENT_3,),
                'person_I_P_M': ("nous " + VERB_CONDITIONAL_PRESENT_4,),
                'person_I_P_F': ("nous " + VERB_CONDITIONAL_PRESENT_4,),
                'person_II_P_M': ("vous " + VERB_CONDITIONAL_PRESENT_5,),
                'person_II_P_F': ("vous " + VERB_CONDITIONAL_PRESENT_5,),
                'person_III_P_M': ("ils " + VERB_CONDITIONAL_PRESENT_6,),
                'persin_III_P_F': ("elles " + VERB_CONDITIONAL_PRESENT_6,),
            }
        },
        'past-first': {
            1: {
                'person_I_S_M': ("j'aurais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'aurais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("tu aurais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu aurais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("il aurait " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle aurait " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("nous aurions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("nous aurions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("vous auriez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("vous auriez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("ils auraient " + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("elles auraient " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {
                'person_I_S_M': ("je serais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("je serais " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("tu serais " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu serais " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("il serait " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle serait " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("nous serions " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("nous serions " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("vous seriez " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("vous seriez " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("ils seraient " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("elles seraient " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
        'past-second': {
            1: {
                'person_I_S_M': ("j'eusse " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("j'eusse " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_M': ("tu eusses " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu eusses " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_M': ("il eût " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle eût " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("nous eussions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("nous eussions " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("vous eussiez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_F': ("vous eussiez " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_P_M': ("ils eussent " + VERB_PAST_PARTICIPLE_S_M,),
                'persin_III_P_F': ("elles eussent " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {

                'person_I_S_M': ("je fusse " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("je fusse " + VERB_PAST_PARTICIPLE_S_F,),
                'person_II_S_M': ("tu fusses " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("tu fusses " + VERB_PAST_PARTICIPLE_S_F,),
                'person_III_S_M': ("il fût " + VERB_PAST_PARTICIPLE_S_M,),
                'person_III_S_F': ("elle fût " + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("nous fussions " + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("nous fussions " + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("vous fussiez " + VERB_PAST_PARTICIPLE_P_M,),
                'person_II_P_F': ("vous fussiez " + VERB_PAST_PARTICIPLE_P_F,),
                'person_III_P_M': ("ils fussent " + VERB_PAST_PARTICIPLE_P_M,),
                'persin_III_P_F': ("elles fussent " + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
    },
    'imperative': {
        'present': {
            1: {
                'person_II_S_M': (VERB_IMPERATIVE_PRESENT_II_S,),
                'person_II_S_F': (VERB_IMPERATIVE_PRESENT_II_S,),
                'person_I_P_M': (VERB_IMPERATIVE_PRESENT_I_P,),
                'person_I_P_F': (VERB_IMPERATIVE_PRESENT_I_P,),
                'person_II_P_M': (VERB_IMPERATIVE_PRESENT_II_P,),
                'persin_II_P_F': (VERB_IMPERATIVE_PRESENT_II_P,),
            },
            2: {
                'person_II_S_M': (VERB_IMPERATIVE_PRESENT_II_S,),
                'person_II_S_F': (VERB_IMPERATIVE_PRESENT_II_S,),
                'person_I_P_M': (VERB_IMPERATIVE_PRESENT_I_P,),
                'person_I_P_F': (VERB_IMPERATIVE_PRESENT_I_P,),
                'person_II_P_M': (VERB_IMPERATIVE_PRESENT_II_P,),
                'persin_II_P_F': (VERB_IMPERATIVE_PRESENT_II_P,),
            },
        },
        'past': {
            1: {
                'person_II_S_M': ("aie " + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("aie " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_M': ("ayons" + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_P_F': ("ayons" + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_P_M': ("ayez" + VERB_PAST_PARTICIPLE_S_M,),
                'persin_II_P_F': ("ayez" + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {
                'person_II_S_M': ("sois" + VERB_PAST_PARTICIPLE_S_M,),
                'person_II_S_F': ("sois" + VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': ("souons" + VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': ("souons" + VERB_PAST_PARTICIPLE_P_F,),
                'person_II_P_M': ("soyez" + VERB_PAST_PARTICIPLE_P_M,),
                'persin_II_P_F': ("soyez" + VERB_PAST_PARTICIPLE_P_F,),
            },
        },
    },
    'participle': {
        'present': {
            1: {
                'person_I_S_M': (VERB_PRESENT_PARTICIPLE,),  # TODO person name?
                'person_I_S_F': (VERB_PRESENT_PARTICIPLE,),  # TODO person name?
            },
            2: {
                'person_I_S_M': (VERB_PRESENT_PARTICIPLE,),  # TODO person name?
                'person_I_S_F': (VERB_PRESENT_PARTICIPLE,),  # TODO person name?
            },
        },
        'past': {
            1: {
                'person_I_S_M': (VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': (VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': (VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': (VERB_PAST_PARTICIPLE_P_F,),
                'person_II_S_M': ("ayant " + VERB_PAST_PARTICIPLE_S_M,),  # TODO person name?
                'person_II_S_F': ("ayant " + VERB_PAST_PARTICIPLE_S_F,),  # TODO person name?
            },
            2: {
                'person_I_S_M': (VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': (VERB_PAST_PARTICIPLE_S_F,),
                'person_I_P_M': (VERB_PAST_PARTICIPLE_P_M,),
                'person_I_P_F': (VERB_PAST_PARTICIPLE_P_F,),
                'person_II_S_M': ("étant " + VERB_PAST_PARTICIPLE_S_M,),  # TODO person name?
                'person_II_S_F': ("étant " + VERB_PAST_PARTICIPLE_S_F,),  # TODO person name?
            }
        }
    },
    'infinitif': {
        'present': {
            1: {
                'person_I_S_M': (VERB_INFINITIVE,),
                'person_I_S_F': (VERB_INFINITIVE,),
            },
            2: {
                'person_I_S_M': (VERB_INFINITIVE,),
                'person_I_S_F': (VERB_INFINITIVE,),
            },
        },
        'past': {
            1: {
                'person_I_S_M': ("avoir " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("avoir " + VERB_PAST_PARTICIPLE_S_M,),
            },
            2: {
                'person_I_S_M': ("être " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("être " + VERB_PAST_PARTICIPLE_S_F,),
            },
        }
    },
    'gerund': {
        'present': {
            1: {
                'person_I_S_M': ("en " + VERB_PRESENT_PARTICIPLE,),
            },
            2: {
                'person_I_S_M': ("en " + VERB_PRESENT_PARTICIPLE,),
            },
        },
        'past': {
            1: {
                'person_I_S_M': ("en ayant " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("en ayant " + VERB_PAST_PARTICIPLE_S_F,),
            },
            2: {
                'person_I_S_M': ("en étant " + VERB_PAST_PARTICIPLE_S_M,),
                'person_I_S_F': ("en étant " + VERB_PAST_PARTICIPLE_S_F,),
            },
        },
    }
}

TEMPLATE_NAME = {
    'indicative': 'Indicatif',
    'present': 'Présent',
    'imperfect': 'Imparfait',
    'simple-past': 'Passé simple',
    'future': 'Futur simple',
    'composé-past': 'Passé composé',
    'pluperfect': 'Plus que parfait',
    'antérieur-past': 'Passé antérieur',
    'antérieur-future': 'Futur antérieur',
    'subjunctive': 'Subjonctif',
    'past': 'Passé',
    'conditional': 'Conditionnel',
    'past-first': 'Passé première forme',
    'past-second': 'Passé deuxième forme',
    'imperative': 'Impératif',
    'infinitif': 'Infinitif',
    'gerund': 'Gérondif',
    'participle': 'Participe'
}


def get_conjugation(request, verb):
    try:
        v = V.objects.get(infinitive=verb)
    except V.DoesNotExist:
        raise Http404('Verb does not exist')
    return JsonResponse(get_conjugations(v))


def get_table(request, verb=None):
    verb_no_accent = unidecode(verb)
    v = V.objects.get(infinitive_no_accents=verb_no_accent)
    table = Table(v)
    template_name = 'conjugation/table.html'
    return render(request, template_name, {'table': table})


def switch_keyboard_layout(s: str):
    LAYOUT_EN = '''`~!@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?'''
    LAYOUT_RU = '''ёЁ!"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'''
    for n in range(LAYOUT_EN.__len__()):
        s = s.replace(LAYOUT_RU[n], LAYOUT_EN[n])
    return s


def get_autocomplete_list(request):
    list_len = 50
    _term = request.GET['term']
    term = unidecode(_term)

    q_startswith = V.objects.filter(
        infinitive_no_accents__startswith=term)  ##.order_by(Length('infinitive').asc())[:list_len]

    if q_startswith.__len__() == 0:
        term = switch_keyboard_layout(_term)
        q_startswith = V.objects.filter(infinitive_no_accents__startswith=term)

    if q_startswith.__len__() < list_len:
        q_contains = V.objects.filter(infinitive_no_accents__contains=term).difference(q_startswith)
        q = list(q_startswith) + list(q_contains)
    else:
        q = q_startswith
    autocomplete_list = []
    term_len = term.__len__()
    for verb in q[0:list_len]:
        pos_start = verb.infinitive_no_accents.find(term)
        pos_end = pos_start + term_len
        html = verb.infinitive[0:pos_start] + '<b>' + verb.infinitive[pos_start:pos_end] + '</b>' + verb.infinitive[
                                                                                                    pos_end:]
        autocomplete_list.append(
            dict(url=reverse('conjugation_verb', args=[verb.infinitive_no_accents]), verbe=verb.infinitive, html=html))
    return JsonResponse(autocomplete_list, safe=False)


class Table:
    def __init__(self, v: V):
        self.v = v
        self.t = v.template
        self.moods = self.get_moods_list()

    def get_moods_list(self):
        moods = []
        for mood_name in FORMULAS.keys():
            mood = Mood(self.v, self.t, mood_name)
            moods.append(mood)
        return moods

    def __str__(self):
        return self.v.infinitive + ' table object'


class Mood:
    def __init__(self, v, t, mood_name):
        self.name = TEMPLATE_NAME[mood_name]
        self.v = v
        self.t = t
        self.mood_name = mood_name
        self.tenses = self.get_tenses_list()

    def get_tenses_list(self):
        tenses = []
        mood_dict = FORMULAS[self.mood_name]
        for tense_name in mood_dict.keys():
            tense = Tense(self.v, self.t, self.mood_name, tense_name)
            tenses.append(tense)
        return tenses

    def __str__(self):
        return self.mood_name


class Tense:
    def __init__(self, v: V, t: T, moode_name, tense_name):
        self.name = TEMPLATE_NAME[tense_name]
        self.v = v
        self.t = t
        self.tense_name = tense_name
        self.mood_name = moode_name
        self.persons = self.get_persons_list()

    def get_persons_list(self):
        persons = []
        tense_dict = FORMULAS[self.mood_name][self.tense_name]
        for person_name in tense_dict[1].keys():
            person = Person(self.v, self.mood_name, self.tense_name, person_name)
            persons.append(person)
        return persons

    def __str__(self):
        return self.tense_name


class Person:
    RED_ENDINGS = {
        'infinitive_infinitive-present': [
            ['er', 'ir', 'ïr', 're']
        ],
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
            ['e'],
            ['ions'],
            ['iez'],
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
    VOWELS = ['a', 'e', 'i', 'o', 'u', 'y', 'â', 'ê', 'è', 'é', 'ô', 'œ', 'î', 'ê','î', 'ï', 'à', 'ä', 'ë', 'ö', 'û','ì']

    def __init__(self, v: V,mood_name: str, tense_name: str, person_name: str, t=None):
        self.v = v
        if t == None or not isinstance(t, T):
            self.t = v.template
        else:
            self.t = t
        self.mood_name = mood_name
        self.tense_name = tense_name
        self.person_name = person_name
        self.formula = self.get_formula()
        if self.formula == None:
            self.part_0 = '-'
            self.part_1 = ''
            self.part_2 = ''
            self.part_3 = ''
        else:
            verb_start = self.v.main_part()
            verb_middle, verb_end = self.get_ends()
            if verb_middle == None and verb_end == None:
                self.part_0 = '-'
                self.part_1 = ''
                self.part_2 = ''
                self.part_3 = ''
            else:
                self.part_1 = verb_start + verb_middle
                self.part_2 = verb_end
                self.part_0 = self.formula.split('+')[0]
                try:
                    self.part_3 = self.formula.split('+')[2]
                except:
                    self.part_3 = ''

    def get_formula(self):
        if self.t.name[0] != ':':
            if self.v.infinitive[0] in self.VOWELS:
                num = -1
            else:
                num = 0
        else:
            path = FORMULAS[self.mood_name][self.tense_name][1][self.person_name][0].split('+')[1].split('_')
            verb = self.t.data[path[0]][path[1]]['p'][int(path[2])]['i']
            if verb == None:
                return None
            if verb[0] in self.VOWELS:
                num = -1
            else:
                num = 0
        if self.v.maison:
            return FORMULAS[self.mood_name][self.tense_name][2][self.person_name][num]
        else:
            return FORMULAS[self.mood_name][self.tense_name][1][self.person_name][num]

    def number(self):
        return len(self.person_name.split('_')[1])

    def plurality(self):
        if self.person_name.split('_')[2] == 'S':
            return 'singular'
        elif self.person_name.split('_')[2] == 'P':
            return 'plural'

    def gender(self):
        if self.person_name.split('_')[3] == 'M':
            return 'male'
        elif self.person_name.split('_')[3] == 'F':
            return 'female'

    def get_ends(self):
        verb_t = self.formula.split('+')[1]
        mood_t, tense_t, n = verb_t.split('_')
        end = self.t.data[mood_t][tense_t]['p'][int(n)]['i']
        if end==None:
            return None, None
        if self.t.no_red_end:
            return '', end
        middle, red_end = self.get_red_end(n, end, mood_t, tense_t)
        return middle, red_end

    def __str__(self):
        return self.person_name

    def get_red_end(self, n, end, mood_name, tense_name):
        if isinstance(end, list):
            end = end[0]
        end_len = end.__len__()
        for red_end in self.RED_ENDINGS[mood_name + '_' + tense_name][int(n)]:
            if end_len < red_end.__len__():
                continue
            else:
                if end.endswith(red_end):
                    middle = end.rsplit(red_end,1)[0]
                    return middle, red_end
        return '', end
