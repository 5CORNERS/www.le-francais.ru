VERB_INFINITIVE = ['infinitive', 'infinitive-present', '0']

VERB_PRESENT_1 = ['indicative', 'present', '0']
VERB_PRESENT_2 = ['indicative', 'present', '1']
VERB_PRESENT_3 = ['indicative', 'present', '2']
VERB_PRESENT_4 = ['indicative', 'present', '3']
VERB_PRESENT_5 = ['indicative', 'present', '4']
VERB_PRESENT_6 = ['indicative', 'present', '5']

VERB_IMPERFECT_1 = ['indicative', 'imperfect', '0']
VERB_IMPERFECT_2 = ['indicative', 'imperfect', '1']
VERB_IMPERFECT_3 = ['indicative', 'imperfect', '2']
VERB_IMPERFECT_4 = ['indicative', 'imperfect', '3']
VERB_IMPERFECT_5 = ['indicative', 'imperfect', '4']
VERB_IMPERFECT_6 = ['indicative', 'imperfect', '5']

VERB_FUTURE_1 = ['indicative', 'future', '0']
VERB_FUTURE_2 = ['indicative', 'future', '1']
VERB_FUTURE_3 = ['indicative', 'future', '2']
VERB_FUTURE_4 = ['indicative', 'future', '3']
VERB_FUTURE_5 = ['indicative', 'future', '4']
VERB_FUTURE_6 = ['indicative', 'future', '5']

VERB_SIMPLE_PAST_1 = ['indicative', 'simple-past', '0']
VERB_SIMPLE_PAST_2 = ['indicative', 'simple-past', '1']
VERB_SIMPLE_PAST_3 = ['indicative', 'simple-past', '2']
VERB_SIMPLE_PAST_4 = ['indicative', 'simple-past', '3']
VERB_SIMPLE_PAST_5 = ['indicative', 'simple-past', '4']
VERB_SIMPLE_PAST_6 = ['indicative', 'simple-past', '5']

VERB_SUBJUNCTIVE_PRESENT_1 = ['subjunctive', 'present', '0']
VERB_SUBJUNCTIVE_PRESENT_2 = ['subjunctive', 'present', '1']
VERB_SUBJUNCTIVE_PRESENT_3 = ['subjunctive', 'present', '2']
VERB_SUBJUNCTIVE_PRESENT_4 = ['subjunctive', 'present', '3']
VERB_SUBJUNCTIVE_PRESENT_5 = ['subjunctive', 'present', '4']
VERB_SUBJUNCTIVE_PRESENT_6 = ['subjunctive', 'present', '5']

VERB_SUBJUNCTIVE_IMPERFECT_1 = ['subjunctive', 'imperfect', '0']
VERB_SUBJUNCTIVE_IMPERFECT_2 = ['subjunctive', 'imperfect', '1']
VERB_SUBJUNCTIVE_IMPERFECT_3 = ['subjunctive', 'imperfect', '2']
VERB_SUBJUNCTIVE_IMPERFECT_4 = ['subjunctive', 'imperfect', '3']
VERB_SUBJUNCTIVE_IMPERFECT_5 = ['subjunctive', 'imperfect', '4']
VERB_SUBJUNCTIVE_IMPERFECT_6 = ['subjunctive', 'imperfect', '5']

VERB_CONDITIONAL_PRESENT_1 = ['conditional', 'present', '0']
VERB_CONDITIONAL_PRESENT_2 = ['conditional', 'present', '1']
VERB_CONDITIONAL_PRESENT_3 = ['conditional', 'present', '2']
VERB_CONDITIONAL_PRESENT_4 = ['conditional', 'present', '3']
VERB_CONDITIONAL_PRESENT_5 = ['conditional', 'present', '4']
VERB_CONDITIONAL_PRESENT_6 = ['conditional', 'present', '5']

VERB_IMPERATIVE_PRESENT_II_S = ['imperative', 'imperative-present', '0']
VERB_IMPERATIVE_PRESENT_I_P = ['imperative', 'imperative-present', '1']
VERB_IMPERATIVE_PRESENT_II_P = ['imperative', 'imperative-present', '2']

VERB_PRESENT_PARTICIPLE = ['participle', 'present-participle', '0']

VERB_PAST_PARTICIPLE_S_M = ['participle', 'past-participle', '0']
VERB_PAST_PARTICIPLE_S_F = ['participle', 'past-participle', '2']
VERB_PAST_PARTICIPLE_P_M = ['participle', 'past-participle', '1']
VERB_PAST_PARTICIPLE_P_F = ['participle', 'past-participle', '3']
FORMULAS = {
    'indicative': {
        'present': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_PRESENT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_PRESENT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_PRESENT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_PRESENT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_PRESENT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_PRESENT_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_PRESENT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_PRESENT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_PRESENT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_PRESENT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_PRESENT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_PRESENT_6,), (('',),),),),
            },
        },
        'simple-past': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_SIMPLE_PAST_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_SIMPLE_PAST_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_SIMPLE_PAST_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_SIMPLE_PAST_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_SIMPLE_PAST_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_SIMPLE_PAST_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_SIMPLE_PAST_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_SIMPLE_PAST_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_SIMPLE_PAST_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_SIMPLE_PAST_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_SIMPLE_PAST_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_SIMPLE_PAST_6,), (('',),),),),
            }
        },
        'composé-past': {
            1: {
                'person_I_S': (((("j'ai ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("tu as ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("il a ",), ("elle a ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("nous avons ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("vous avez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("ils ont ",), ("elles ont ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {

                'person_I_S': (((("je suis ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("tu es ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("il est ",), ("elle est ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("nous sommes ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("vous êtes ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("ils sont ",), ("elles sont ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
        'antérieur-past': {
            1: {
                'person_I_S': (((("j'eus ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("tu eus ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("il eut ",), ("elle eut ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("nous eûmes ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("vous eûtes ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("ils eurent ",), ("elles eurent ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je fus ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("tu fus ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("il fut ",), ("elle fut ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("nous fûmes ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("vous fûtes ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("ils furent ",), ("elles furent ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
        'imperfect': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_IMPERFECT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_IMPERFECT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_IMPERFECT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_IMPERFECT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_IMPERFECT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_IMPERFECT_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_IMPERFECT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_IMPERFECT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_IMPERFECT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_IMPERFECT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_IMPERFECT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_IMPERFECT_6,), (('',),),),),
            },
        },
        'future': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_FUTURE_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_FUTURE_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_FUTURE_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_FUTURE_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_FUTURE_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_FUTURE_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_FUTURE_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_FUTURE_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_FUTURE_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_FUTURE_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_FUTURE_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_FUTURE_6,), (('',),),),),
            }
        },
        'pluperfect': {
            1: {
                'person_I_S': (((("j'avais ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("tu avais ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("il avait ",), ('elle avait',),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("nous avions ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("vous aviez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("ils avaient ",), ('elles avaient',),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {
                'person_I_S': (((("j'étais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("tu étais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("il était ",), ('elle était',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("nous étions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("vous étiez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("ils étaient ",), ('elles étaient',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
        'antérieur-future': {
            1: {
                'person_I_S': (((("j'aurai ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("tu auras ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("il aura ",), ("elle aura ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("nous aurons ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("vous aurez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("ils auront ",), ("elles auront ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je serai ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("tu seras ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("il sera ",), ("elle sera ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("nous serons ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("vous serez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("ils seront ",), ("elles seront ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
    },
    'subjunctive': {
        'present': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_SUBJUNCTIVE_PRESENT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_SUBJUNCTIVE_PRESENT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_SUBJUNCTIVE_PRESENT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_SUBJUNCTIVE_PRESENT_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_SUBJUNCTIVE_PRESENT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_SUBJUNCTIVE_PRESENT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_SUBJUNCTIVE_PRESENT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_SUBJUNCTIVE_PRESENT_6,), (('',),),),),
            },
        },
        'past': {
            1: {
                'person_I_S': (((("que j'aie ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("que tu aies ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("qu'il ait ",), ("qu'elle ait ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("que nous ayons ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("que vous ayez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("qu'ils aient ",), ("qu'elles aient ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {

                'person_I_S': (((("que je sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("que tu sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("qu'il soit ",), ("qu'elle soit ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("que nous soyons ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("que vous soyez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("qu'ils soient ",), ("qu'elles soient ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
        'imperfect': {
            1: {
                'person_I_S': (((("que je ", "que j'",),), (VERB_SUBJUNCTIVE_IMPERFECT_1,), (('',),),),),
                'person_II_S': (((("que tu ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2,), (('',),),),),
                'person_III_S': (((("qu'il ",), ("qu'elle ",),), (VERB_SUBJUNCTIVE_IMPERFECT_3,), (('',),),),),
                'person_I_P': (((("que nous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4,), (('',),),),),
                'person_II_P': (((("que vous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5,), (('',),),),),
                'person_III_P': (((("qu'ils ",), ("qu'elles ",),), (VERB_SUBJUNCTIVE_IMPERFECT_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("que je ", "que j'",),), (VERB_SUBJUNCTIVE_IMPERFECT_1,), (('',),),),),
                'person_II_S': (((("que tu ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2,), (('',),),),),
                'person_III_S': (((("qu'il ",), ("qu'elle ",),), (VERB_SUBJUNCTIVE_IMPERFECT_3,), (('',),),),),
                'person_I_P': (((("que nous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4,), (('',),),),),
                'person_II_P': (((("que vous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5,), (('',),),),),
                'person_III_P': (((("qu'ils ",), ("qu'elles ",),), (VERB_SUBJUNCTIVE_IMPERFECT_6,), (('',),),),),
            },
        },
        'pluperfect': {
            1: {
                'person_I_S': (((("que j'eusse ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("que tu eusses ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("qu'il eût ",), ("qu'elle eût ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("que nous eussions ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("que vous eussiez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("qu'ils eussent ",), ("qu'elles eussent ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {
                'person_I_S': (((("que je fusse ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("que tu fusses ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("qu'il fût ",), ("qu'elle fût ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("que nous fussions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("que vous fussiez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("qu'ils fussent ",), ("qu'elles fussent ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
    },
    'conditional': {
        'present': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_CONDITIONAL_PRESENT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_CONDITIONAL_PRESENT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_CONDITIONAL_PRESENT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_CONDITIONAL_PRESENT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_CONDITIONAL_PRESENT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_CONDITIONAL_PRESENT_6,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_CONDITIONAL_PRESENT_1,), (('',),),),),
                'person_II_S': (((("tu ",),), (VERB_CONDITIONAL_PRESENT_2,), (('',),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_CONDITIONAL_PRESENT_3,), (('',),),),),
                'person_I_P': (((("nous ",),), (VERB_CONDITIONAL_PRESENT_4,), (('',),),),),
                'person_II_P': (((("vous ",),), (VERB_CONDITIONAL_PRESENT_5,), (('',),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_CONDITIONAL_PRESENT_6,), (('',),),),),
            }
        },
        'past-first': {
            1: {
                'person_I_S': (((("j'aurais ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_S': (((("tu aurais ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_S': (((("il aurait ",), ("elle aurait ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("nous aurions ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_II_P': (((("vous auriez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_III_P': (((("ils auraient ",), ("elles auraient ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {
                'person_I_S': (((("je serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_II_S': (((("tu serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_III_S': (((("il serait ",), ("elle serait ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("nous serions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("vous seriez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_III_P': (((("ils seraient ",), ("elles seraient ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
        # 'past-second': {
        #     1: {
        #         'person_I_S': (((("j'eusse ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
        #         'person_II_S': (((("tu eusses ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
        #         'person_III_S': (((("il eût ",), ("elle eût ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
        #         'person_I_P': (((("nous eussions ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
        #         'person_II_P': (((("vous eussiez ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
        #         'person_III_P': (((("ils eussent ",), ("elles eussent ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
        #     },
        #     2: {
        #         'person_I_S': (((("je fusse ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
        #         'person_II_S': (((("tu fusses ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
        #         'person_III_S': (((("il fût ",), ("elle fût ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
        #         'person_I_P': (((("nous fussions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
        #         'person_II_P': (((("vous fussiez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
        #         'person_III_P': (((("ils fussent ",), ("elles fussent ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
        #     },
        # },
    },
    'imperative': {
        'present': {
            1: {
                'person_II_S': (((('',),), (VERB_IMPERATIVE_PRESENT_II_S,), (('',),),),),
                'person_I_P': (((('',),), (VERB_IMPERATIVE_PRESENT_I_P,), (('',),),),),
                'person_II_P': (((('',),), (VERB_IMPERATIVE_PRESENT_II_P,), (('',),),),),
            },
            2: {
                'person_II_S': (((('',),), (VERB_IMPERATIVE_PRESENT_II_S,), (('',),),),),
                'person_I_P': (((('',),), (VERB_IMPERATIVE_PRESENT_I_P,), (('',),),),),
                'person_II_P': (((('',),), (VERB_IMPERATIVE_PRESENT_II_P,), (('',),),),),
            },
        },
        'past': {
            1: {
                'person_II_S': (((("aie ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
                'person_I_P': (((("ayons ",),), (VERB_PAST_PARTICIPLE_P_M,), (('',),),),),
                'person_II_P': (((("ayez ",),), (VERB_PAST_PARTICIPLE_P_M,), (('',),),),),
            },
            2: {
                'person_II_S': (((("sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((("souons ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_P': (((("soyez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
            },
        },
    },
    'participle': {
        'present': {
            1: {
                'person_I_S': (((('',),), (VERB_PRESENT_PARTICIPLE,), (('',),),),),  # (TODO person name?,)
            },
            2: {
                'person_I_S': (((('',),), (VERB_PRESENT_PARTICIPLE,), (('',),),),),  # (TODO person name?,)
            },
        },
        'past': {
            1: {
                'person_I_S': (((('',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((('',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_S': (((("ayant ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),  # (TODO person name?,)
            },
            2: {
                'person_I_S': (((('',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
                'person_I_P': (((('',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),),
                'person_II_S': (((("étant ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),  # (TODO person name?,)
            }
        }
    },
    'infinitive': {
        'present': {
            1: {
                'person_I_S': (((("",),), (VERB_INFINITIVE,), (('',),),),),
            },
            2: {
                'person_I_S': (((("",),), (VERB_INFINITIVE,), (('',),),),),
            },
        },
        'past': {
            1: {
                'person_I_S': (((("avoir ",),), (VERB_PAST_PARTICIPLE_S_M,), (('',),),),),
            },
            2: {
                'person_I_S': (((("être ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
            },
        }
    },
    'gerund': {
        'present': {
            1: {
                'person_I_S': (((("en ",),), (VERB_PRESENT_PARTICIPLE,), (('',),),),),
            },
            2: {
                'person_I_S': (((("en ",),), (VERB_PRESENT_PARTICIPLE,), (('',),),),),
            },
        },
        'past': {
            1: {
                'person_I_S': (((("en ayant ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
            },
            2: {
                'person_I_S': (((("en étant ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),),
            },
        },
    }
}

FORMULAS_PASSIVE = {'indicative': {'present': {1: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_PRESENT_1, VERB_PRESENT_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_PRESENT_2, VERB_PRESENT_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ('elle se ', "elle s'",),), (VERB_PRESENT_3, VERB_PRESENT_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_PRESENT_4, VERB_PRESENT_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_PRESENT_5, VERB_PRESENT_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ('elles se ', "elles s'",),), (VERB_PRESENT_6, VERB_PRESENT_6,), (('',),),),)}, 2: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_PRESENT_1, VERB_PRESENT_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_PRESENT_2, VERB_PRESENT_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ('elle se ', "elle s'",),), (VERB_PRESENT_3, VERB_PRESENT_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_PRESENT_4, VERB_PRESENT_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_PRESENT_5, VERB_PRESENT_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ('elles se ', "elles s'",),), (VERB_PRESENT_6, VERB_PRESENT_6,), (('',),),),)}}, 'composé-past': {1: {'person_I_S': (((('je me suis ', 'je me suis',), ('je me suis ', 'je me suis',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((("tu t'es ", "tu t'es",), ("tu t'es ", "tu t'es",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("il s'est ", "il s'est",), ("elle s'est ", "elle s'est",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous sommes ', 'nous nous sommes',), ('nous nous sommes ', 'nous nous sommes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous êtes ', 'vous vous êtes',), ('vous vous êtes ', 'vous vous êtes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se sont ', 'ils se sont',), ('elles se sont ', 'elles se sont',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('je me suis ', 'je me suis',), ('je me suis ', 'je me suis',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((("tu t'es ", "tu t'es",), ("tu t'es ", "tu t'es",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("il s'est ", "il s'est",), ("elle s'est ", "elle s'est",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous sommes ', 'nous nous sommes',), ('nous nous sommes ', 'nous nous sommes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous êtes ', 'vous vous êtes',), ('vous vous êtes ', 'vous vous êtes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se sont ', 'ils se sont',), ('elles se sont ', 'elles se sont',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}, 'imperfect': {1: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_IMPERFECT_1, VERB_IMPERFECT_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_IMPERFECT_2, VERB_IMPERFECT_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ('elle se ', "elle s'",),), (VERB_IMPERFECT_3, VERB_IMPERFECT_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_IMPERFECT_4, VERB_IMPERFECT_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_IMPERFECT_5, VERB_IMPERFECT_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ('elles se ', "elles s'",),), (VERB_IMPERFECT_6, VERB_IMPERFECT_6,), (('',),),),)}, 2: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_IMPERFECT_1, VERB_IMPERFECT_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_IMPERFECT_2, VERB_IMPERFECT_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ('elle se ', "elle s'",),), (VERB_IMPERFECT_3, VERB_IMPERFECT_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_IMPERFECT_4, VERB_IMPERFECT_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_IMPERFECT_5, VERB_IMPERFECT_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ('elles se ', "elles s'",),), (VERB_IMPERFECT_6, VERB_IMPERFECT_6,), (('',),),),)}}, 'pluperfect': {1: {'person_I_S': (((("je m'étais ", "je m'étais",), ("je m'étais ", "je m'étais",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((("tu t'étais ", "tu t'étais",), ("tu t'étais ", "tu t'étais",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("il s'était ", "il s'était",), ("elle s'était ", "elle s'était",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous étions ', 'nous nous étions',), ('nous nous étions ', 'nous nous étions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous étiez ', 'vous vous étiez',), ('vous vous étiez ', 'vous vous étiez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((("ils s'étaient ", "ils s'étaient",), ("elles s'étaient ", "elles s'étaient",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((("je m'étais ", "je m'étais",), ("je m'étais ", "je m'étais",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((("tu t'étais ", "tu t'étais",), ("tu t'étais ", "tu t'étais",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("il s'était ", "il s'était",), ("elle s'était ", "elle s'était",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous étions ', 'nous nous étions',), ('nous nous étions ', 'nous nous étions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous étiez ', 'vous vous étiez',), ('vous vous étiez ', 'vous vous étiez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((("ils s'étaient ", "ils s'étaient",), ("elles s'étaient ", "elles s'étaient",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}, 'simple-past': {1: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_SIMPLE_PAST_1, VERB_SIMPLE_PAST_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_SIMPLE_PAST_2, VERB_SIMPLE_PAST_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ("elle s'", "elle s'",),), (VERB_SIMPLE_PAST_3, VERB_SIMPLE_PAST_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_SIMPLE_PAST_4, VERB_SIMPLE_PAST_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_SIMPLE_PAST_5, VERB_SIMPLE_PAST_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ("elles s'", "elles s'",),), (VERB_SIMPLE_PAST_6, VERB_SIMPLE_PAST_6,), (('',),),),)}, 2: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_SIMPLE_PAST_1, VERB_SIMPLE_PAST_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_SIMPLE_PAST_2, VERB_SIMPLE_PAST_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ("elle s'", "elle s'",),), (VERB_SIMPLE_PAST_3, VERB_SIMPLE_PAST_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_SIMPLE_PAST_4, VERB_SIMPLE_PAST_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_SIMPLE_PAST_5, VERB_SIMPLE_PAST_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ("elles s'", "elles s'",),), (VERB_SIMPLE_PAST_6, VERB_SIMPLE_PAST_6,), (('',),),),)}}, 'antérieur-past': {1: {'person_I_S': (((('je me fus ', 'je me fus',), ('je me fus ', 'je me fus',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te fus ', 'tu te fus',), ('tu te fus ', 'tu te fus',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se fut ', 'il se fut',), ('elle se fut ', 'elle se fut',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous fûmes ', 'nous nous fûmes',), ('nous nous fûmes ', 'nous nous fûmes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous fûtes ', 'vous vous fûtes',), ('vous vous fûtes ', 'vous vous fûtes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se furent ', 'ils se furent',), ('elles se furent ', 'elles se furent',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('je me fus ', 'je me fus',), ('je me fus ', 'je me fus',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te fus ', 'tu te fus',), ('tu te fus ', 'tu te fus',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se fut ', 'il se fut',), ('elle se fut ', 'elle se fut',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous fûmes ', 'nous nous fûmes',), ('nous nous fûmes ', 'nous nous fûmes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous fûtes ', 'vous vous fûtes',), ('vous vous fûtes ', 'vous vous fûtes',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se furent ', 'ils se furent',), ('elles se furent ', 'elles se furent',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}, 'future': {1: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_FUTURE_1, VERB_FUTURE_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_FUTURE_2, VERB_FUTURE_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ("elle s'", "elle s'",),), (VERB_FUTURE_3, VERB_FUTURE_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_FUTURE_4, VERB_FUTURE_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_FUTURE_5, VERB_FUTURE_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ("elles s'", "elles s'",),), (VERB_FUTURE_6, VERB_FUTURE_6,), (('',),),),)}, 2: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_FUTURE_1, VERB_FUTURE_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_FUTURE_2, VERB_FUTURE_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ("elle s'", "elle s'",),), (VERB_FUTURE_3, VERB_FUTURE_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_FUTURE_4, VERB_FUTURE_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_FUTURE_5, VERB_FUTURE_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ("elles s'", "elles s'",),), (VERB_FUTURE_6, VERB_FUTURE_6,), (('',),),),)}}, 'antérieur-future': {1: {'person_I_S': (((('je me serai ', 'je me serai',), ('je me serai ', 'je me serai',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te seras ', 'tu te seras',), ('tu te seras ', 'tu te seras',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se sera ', 'il se sera',), ('elle se sera ', 'elle se sera',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous serons ', 'nous nous serons',), ('nous nous serons ', 'nous nous serons',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous serez ', 'vous vous serez',), ('vous vous serez ', 'vous vous serez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se seront ', 'ils se seront',), ('elles se seront ', 'elles se seront',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('je me serai ', 'je me serai',), ('je me serai ', 'je me serai',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te seras ', 'tu te seras',), ('tu te seras ', 'tu te seras',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se sera ', 'il se sera',), ('elle se sera ', 'elle se sera',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous serons ', 'nous nous serons',), ('nous nous serons ', 'nous nous serons',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous serez ', 'vous vous serez',), ('vous vous serez ', 'vous vous serez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se seront ', 'ils se seront',), ('elles se seront ', 'elles se seront',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}}, 'subjunctive': {'present': {1: {'person_I_S': (((('que je me ', "que je m'",), ('que je me ', 'que je me',),), (VERB_SUBJUNCTIVE_PRESENT_1, VERB_SUBJUNCTIVE_PRESENT_1,), (('',),),),), 'person_II_S': (((('que tu te ', "que tu t'",), ('que tu te ', 'que tu te',),), (VERB_SUBJUNCTIVE_PRESENT_2, VERB_SUBJUNCTIVE_PRESENT_2,), (('',),),),), 'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle s'", "qu'elle s'",),), (VERB_SUBJUNCTIVE_PRESENT_3, VERB_SUBJUNCTIVE_PRESENT_3,), (('',),),),), 'person_I_P': (((('que nous nous ', 'que nous nous',), ('que nous nous ', 'que nous nous',),), (VERB_SUBJUNCTIVE_PRESENT_4, VERB_SUBJUNCTIVE_PRESENT_4,), (('',),),),), 'person_II_P': (((('que vous vous ', 'que vous vous',), ('que vous vous ', 'que vous vous',),), (VERB_SUBJUNCTIVE_PRESENT_5, VERB_SUBJUNCTIVE_PRESENT_5,), (('',),),),), 'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles s'", "qu'elles s'",),), (VERB_SUBJUNCTIVE_PRESENT_6, VERB_SUBJUNCTIVE_PRESENT_6,), (('',),),),)}, 2: {'person_I_S': (((('que je me ', "que je m'",), ('que je me ', 'que je me',),), (VERB_SUBJUNCTIVE_PRESENT_1, VERB_SUBJUNCTIVE_PRESENT_1,), (('',),),),), 'person_II_S': (((('que tu te ', "que tu t'",), ('que tu te ', 'que tu te',),), (VERB_SUBJUNCTIVE_PRESENT_2, VERB_SUBJUNCTIVE_PRESENT_2,), (('',),),),), 'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle s'", "qu'elle s'",),), (VERB_SUBJUNCTIVE_PRESENT_3, VERB_SUBJUNCTIVE_PRESENT_3,), (('',),),),), 'person_I_P': (((('que nous nous ', 'que nous nous',), ('que nous nous ', 'que nous nous',),), (VERB_SUBJUNCTIVE_PRESENT_4, VERB_SUBJUNCTIVE_PRESENT_4,), (('',),),),), 'person_II_P': (((('que vous vous ', 'que vous vous',), ('que vous vous ', 'que vous vous',),), (VERB_SUBJUNCTIVE_PRESENT_5, VERB_SUBJUNCTIVE_PRESENT_5,), (('',),),),), 'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles s'", "qu'elles s'",),), (VERB_SUBJUNCTIVE_PRESENT_6, VERB_SUBJUNCTIVE_PRESENT_6,), (('',),),),)}}, 'past': {1: {'person_I_S': (((('que je me sois ', 'que je me sois',), ('que je me sois ', 'que je me sois',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('que tu te sois ', 'que tu te sois',), ('que tu te sois ', 'que tu te sois',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("qu'il se soit ", "qu'il se soit",), ("qu'elle se soit ", "qu'elle se soit",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('que nous nous soyons ', 'que nous nous soyons',), ('que nous nous soyons ', 'que nous nous soyons',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('que vous vous soyez ', 'que vous vous soyez',), ('que vous vous soyez ', 'que vous vous soyez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((("qu'ils se soient ", "qu'ils se soient",), ("qu'elles se soient ", "qu'elles se soient",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('que je me sois ', 'que je me sois',), ('que je me sois ', 'que je me sois',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('que tu te sois ', 'que tu te sois',), ('que tu te sois ', 'que tu te sois',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("qu'il se soit ", "qu'il se soit",), ("qu'elle se soit ", "qu'elle se soit",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('que nous nous soyons ', 'que nous nous soyons',), ('que nous nous soyons ', 'que nous nous soyons',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('que vous vous soyez ', 'que vous vous soyez',), ('que vous vous soyez ', 'que vous vous soyez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((("qu'ils se soient ", "qu'ils se soient",), ("qu'elles se soient ", "qu'elles se soient",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}, 'imperfect': {1: {'person_I_S': (((('que je me ', "que je m'",), ('que je me ', 'que je me',),), (VERB_SUBJUNCTIVE_IMPERFECT_1, VERB_SUBJUNCTIVE_IMPERFECT_1,), (('',),),),), 'person_II_S': (((('que tu te ', "que tu t'",), ('que tu te ', 'que tu te',),), (VERB_SUBJUNCTIVE_IMPERFECT_2, VERB_SUBJUNCTIVE_IMPERFECT_2,), (('',),),),), 'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle s'", "qu'elle s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_3, VERB_SUBJUNCTIVE_IMPERFECT_3,), (('',),),),), 'person_I_P': (((('que nous nous ', 'que nous nous',), ('que nous nous ', 'que nous nous',),), (VERB_SUBJUNCTIVE_IMPERFECT_4, VERB_SUBJUNCTIVE_IMPERFECT_4,), (('',),),),), 'person_II_P': (((('que vous vous ', 'que vous vous',), ('que vous vous ', 'que vous vous',),), (VERB_SUBJUNCTIVE_IMPERFECT_5, VERB_SUBJUNCTIVE_IMPERFECT_5,), (('',),),),), 'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles s'", "qu'elles s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_6, VERB_SUBJUNCTIVE_IMPERFECT_6,), (('',),),),)}, 2: {'person_I_S': (((('que je me ', "que je m'",), ('que je me ', 'que je me',),), (VERB_SUBJUNCTIVE_IMPERFECT_1, VERB_SUBJUNCTIVE_IMPERFECT_1,), (('',),),),), 'person_II_S': (((('que tu te ', "que tu t'",), ('que tu te ', 'que tu te',),), (VERB_SUBJUNCTIVE_IMPERFECT_2, VERB_SUBJUNCTIVE_IMPERFECT_2,), (('',),),),), 'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle s'", "qu'elle s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_3, VERB_SUBJUNCTIVE_IMPERFECT_3,), (('',),),),), 'person_I_P': (((('que nous nous ', 'que nous nous',), ('que nous nous ', 'que nous nous',),), (VERB_SUBJUNCTIVE_IMPERFECT_4, VERB_SUBJUNCTIVE_IMPERFECT_4,), (('',),),),), 'person_II_P': (((('que vous vous ', 'que vous vous',), ('que vous vous ', 'que vous vous',),), (VERB_SUBJUNCTIVE_IMPERFECT_5, VERB_SUBJUNCTIVE_IMPERFECT_5,), (('',),),),), 'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles s'", "qu'elles s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_6, VERB_SUBJUNCTIVE_IMPERFECT_6,), (('',),),),)}}, 'pluperfect': {1: {'person_I_S': (((('que je me fusse ', 'que je me fusse',), ('que je me fusse ', 'que je me fusse',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('que tu te fusses ', 'que tu te fusses',), ('que tu te fusses ', 'que tu te fusses',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("qu'il se fût ", "qu'il se fût",), ("qu'elle se fût ", "qu'elle se fût",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('que nous nous fussions ', 'que nous nous fussions',), ('que nous nous fussions ', 'que nous nous fussions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('que vous vous fussiez ', 'que vous vous fussiez',), ('que vous vous fussiez ', 'que vous vous fussiez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((("qu'ils se fussent ", "qu'ils se fussent",), ("qu'elles se fussent ", "qu'elles se fussent",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('que je me fusse ', 'que je me fusse',), ('que je me fusse ', 'que je me fusse',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('que tu te fusses ', 'que tu te fusses',), ('que tu te fusses ', 'que tu te fusses',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((("qu'il se fût ", "qu'il se fût",), ("qu'elle se fût ", "qu'elle se fût",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('que nous nous fussions ', 'que nous nous fussions',), ('que nous nous fussions ', 'que nous nous fussions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('que vous vous fussiez ', 'que vous vous fussiez',), ('que vous vous fussiez ', 'que vous vous fussiez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((("qu'ils se fussent ", "qu'ils se fussent",), ("qu'elles se fussent ", "qu'elles se fussent",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}}, 'conditional': {'present': {1: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_CONDITIONAL_PRESENT_1, VERB_CONDITIONAL_PRESENT_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_CONDITIONAL_PRESENT_2, VERB_CONDITIONAL_PRESENT_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ("elle s'", "elle s'",),), (VERB_CONDITIONAL_PRESENT_3, VERB_CONDITIONAL_PRESENT_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_CONDITIONAL_PRESENT_4, VERB_CONDITIONAL_PRESENT_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_CONDITIONAL_PRESENT_5, VERB_CONDITIONAL_PRESENT_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ("elles s'", "elles s'",),), (VERB_CONDITIONAL_PRESENT_6, VERB_CONDITIONAL_PRESENT_6,), (('',),),),)}, 2: {'person_I_S': (((('je me ', "je m'",), ('je me ', 'je me',),), (VERB_CONDITIONAL_PRESENT_1, VERB_CONDITIONAL_PRESENT_1,), (('',),),),), 'person_II_S': (((('tu te ', "tu t'",), ('tu te ', 'tu te',),), (VERB_CONDITIONAL_PRESENT_2, VERB_CONDITIONAL_PRESENT_2,), (('',),),),), 'person_III_S': (((('il se ', "il s'",), ("elle s'", "elle s'",),), (VERB_CONDITIONAL_PRESENT_3, VERB_CONDITIONAL_PRESENT_3,), (('',),),),), 'person_I_P': (((('nous nous ', 'nous nous',), ('nous nous ', 'nous nous',),), (VERB_CONDITIONAL_PRESENT_4, VERB_CONDITIONAL_PRESENT_4,), (('',),),),), 'person_II_P': (((('vous vous ', 'vous vous',), ('vous vous ', 'vous vous',),), (VERB_CONDITIONAL_PRESENT_5, VERB_CONDITIONAL_PRESENT_5,), (('',),),),), 'person_III_P': (((('ils se ', "ils s'",), ("elles s'", "elles s'",),), (VERB_CONDITIONAL_PRESENT_6, VERB_CONDITIONAL_PRESENT_6,), (('',),),),)}}, 'past-first': {1: {'person_I_S': (((('je me serais ', 'je me serais',), ('je me serais ', 'je me serais',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te serais ', 'tu te serais',), ('tu te serais ', 'tu te serais',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se serait ', 'il se serait',), ('elle se serait ', 'elle se serait',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous serions ', 'nous nous serions',), ('nous nous serions ', 'nous nous serions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous seriez ', 'vous vous seriez',), ('vous vous seriez ', 'vous vous seriez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se seraient ', 'ils se seraient',), ('elles se seraient ', 'elles se seraient',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('je me serais ', 'je me serais',), ('je me serais ', 'je me serais',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te serais ', 'tu te serais',), ('tu te serais ', 'tu te serais',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se serait ', 'il se serait',), ('elle se serait ', 'elle se serait',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous serions ', 'nous nous serions',), ('nous nous serions ', 'nous nous serions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous seriez ', 'vous vous seriez',), ('vous vous seriez ', 'vous vous seriez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se seraient ', 'ils se seraient',), ('elles se seraient ', 'elles se seraient',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}},
# 'past-second': {1: {'person_I_S': (((('je me fusse ', 'je me fusse',), ('je me fusse ', 'je me fusse',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te fusses ', 'tu te fusses',), ('tu te fusses ', 'tu te fusses',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se fût ', 'il se fût',), ('elle se fût ', 'elle se fût',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous fussions ', 'nous nous fussions',), ('nous nous fussions ', 'nous nous fussions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous fussiez ', 'vous vous fussiez',), ('vous vous fussiez ', 'vous vous fussiez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se fussent ', 'ils se fussent',), ('elles se fussent ', 'elles se fussent',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}, 2: {'person_I_S': (((('je me fusse ', 'je me fusse',), ('je me fusse ', 'je me fusse',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_II_S': (((('tu te fusses ', 'tu te fusses',), ('tu te fusses ', 'tu te fusses',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_III_S': (((('il se fût ', 'il se fût',), ('elle se fût ', 'elle se fût',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': (((('nous nous fussions ', 'nous nous fussions',), ('nous nous fussions ', 'nous nous fussions',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_P': (((('vous vous fussiez ', 'vous vous fussiez',), ('vous vous fussiez ', 'vous vous fussiez',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_III_P': (((('ils se fussent ', 'ils se fussent',), ('elles se fussent ', 'elles se fussent',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),)}}
}, 'imperative': {'present': {1: {'person_II_S': ((((' ', '',), (' ', '',),), (VERB_IMPERATIVE_PRESENT_II_S, VERB_IMPERATIVE_PRESENT_II_S,), (('-toi',),),),), 'person_I_P': ((((' ', '',), (' ', '',),), (VERB_IMPERATIVE_PRESENT_I_P, VERB_IMPERATIVE_PRESENT_I_P,), (('-nous',),),),), 'person_II_P': ((((' ', '',), (' ', '',),), (VERB_IMPERATIVE_PRESENT_II_P, VERB_IMPERATIVE_PRESENT_II_P,), (('-vous',),),),)}, 2: {'person_II_S': ((((' ', '',), (' ', '',),), (VERB_IMPERATIVE_PRESENT_II_S, VERB_IMPERATIVE_PRESENT_II_S,), (('-toi',),),),), 'person_I_P': ((((' ', '',), (' ', '',),), (VERB_IMPERATIVE_PRESENT_I_P, VERB_IMPERATIVE_PRESENT_I_P,), (('-nous',),),),), 'person_II_P': ((((' ', '',), (' ', '',),), (VERB_IMPERATIVE_PRESENT_II_P, VERB_IMPERATIVE_PRESENT_II_P,), (('-vous',),),),)}}, 'past': {1: {'person_II_S': ((((' ', '',), (' ', '',),), (None, None,), (('',),),),), 'person_I_P': ((((' ', '',), (' ', '',),), (None, None,), (('',),),),), 'person_II_P': ((((' ', '',), (' ', '',),), (None, None,), (('',),),),)}, 2: {'person_II_S': ((((' ', '',), (' ', '',),), (None, None,), (('',),),),), 'person_I_P': ((((' ', '',), (' ', '',),), (None, None,), (('',),),),), 'person_II_P': ((((' ', '',), (' ', '',),), (None, None,), (('',),),),)}}}, 'participle': {'present': {1: {'person_I_S': (((('se ', "s'",), ('se ', 'se',),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (('',),),),)}, 2: {'person_I_S': (((('se ', "s'",), ('se ', 'se',),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (('',),),),)}}, 'past': {1: {'person_I_S': ((((' ', '',), (' ', '',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': ((((' ', '',), (' ', '',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_S': (((("s'étant ", "s'étant",), ("s'étant ", "s'étant",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),)}, 2: {'person_I_S': ((((' ', '',), (' ', '',),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),), 'person_I_P': ((((' ', '',), (' ', '',),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (('',),),),), 'person_II_S': (((("s'étant ", "s'étant",), ("s'étant ", "s'étant",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (('',),),),)}}}, 'infinitive': {'present': {1: {'person_I_S': (((('se ', "s'",), ('se ', 'se',),), (VERB_INFINITIVE, VERB_INFINITIVE,), (('',),),),)}, 2: {'person_I_S': (((('se ', "s'",), ('se ', 'se',),), (VERB_INFINITIVE, VERB_INFINITIVE,), (('',),),),)}}, 'past': {1: {'person_I_S': (((("s'être ", "s'être",), ("s'être ", "s'être",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (('',),),),)}, 2: {'person_I_S': (((("s'être ", "s'être",), ("s'être ", "s'être",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (('',),),),)}}}, 'gerund': {'present': {1: {'person_I_S': (((('en se ', "en s'",), ('en se ', 'en se',),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (('',),),),)}, 2: {'person_I_S': (((('en se ', "en s'",), ('en se ', 'en se',),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (('',),),),)}}, 'past': {1: {'person_I_S': (((("en s'étant ", "en s'étant",), ("en s'étant ", "en s'étant",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (('',),),),)}, 2: {'person_I_S': (((("en s'étant ", "en s'étant",), ("en s'étant ", "en s'étant",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (('',),),),)}}}}

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
    'past-first': 'Passé',
    'past-second': 'Passé deuxième forme',
    'imperative': 'Impératif',
    'infinitive': 'Infinitif',
    'gerund': 'Gérondif',
    'participle': 'Participe'
}

SHORT_LIST = {
    'indicative':['simple-past','antérieur-past'],
    'subjunctive':['imperfect','pluperfect'],
    'conditional':['past-second'],
    'imperative':['past'],
    'gerund':[],
    'infinitive':[],
    'participle':[],
}
