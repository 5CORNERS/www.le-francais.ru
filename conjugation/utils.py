VERB_INFINITIVE = ["infinitive", "infinitive-present", "0"]

VERB_PRESENT_1 = ["indicative", "present", "0"]
VERB_PRESENT_2 = ["indicative", "present", "1"]
VERB_PRESENT_3 = ["indicative", "present", "2"]
VERB_PRESENT_4 = ["indicative", "present", "3"]
VERB_PRESENT_5 = ["indicative", "present", "4"]
VERB_PRESENT_6 = ["indicative", "present", "5"]

VERB_IMPERFECT_1 = ["indicative", "imperfect", "0"]
VERB_IMPERFECT_2 = ["indicative", "imperfect", "1"]
VERB_IMPERFECT_3 = ["indicative", "imperfect", "2"]
VERB_IMPERFECT_4 = ["indicative", "imperfect", "3"]
VERB_IMPERFECT_5 = ["indicative", "imperfect", "4"]
VERB_IMPERFECT_6 = ["indicative", "imperfect", "5"]

VERB_FUTURE_1 = ["indicative", "future", "0"]
VERB_FUTURE_2 = ["indicative", "future", "1"]
VERB_FUTURE_3 = ["indicative", "future", "2"]
VERB_FUTURE_4 = ["indicative", "future", "3"]
VERB_FUTURE_5 = ["indicative", "future", "4"]
VERB_FUTURE_6 = ["indicative", "future", "5"]

VERB_SIMPLE_PAST_1 = ["indicative", "simple-past", "0"]
VERB_SIMPLE_PAST_2 = ["indicative", "simple-past", "1"]
VERB_SIMPLE_PAST_3 = ["indicative", "simple-past", "2"]
VERB_SIMPLE_PAST_4 = ["indicative", "simple-past", "3"]
VERB_SIMPLE_PAST_5 = ["indicative", "simple-past", "4"]
VERB_SIMPLE_PAST_6 = ["indicative", "simple-past", "5"]

VERB_SUBJUNCTIVE_PRESENT_1 = ["subjunctive", "present", "0"]
VERB_SUBJUNCTIVE_PRESENT_2 = ["subjunctive", "present", "1"]
VERB_SUBJUNCTIVE_PRESENT_3 = ["subjunctive", "present", "2"]
VERB_SUBJUNCTIVE_PRESENT_4 = ["subjunctive", "present", "3"]
VERB_SUBJUNCTIVE_PRESENT_5 = ["subjunctive", "present", "4"]
VERB_SUBJUNCTIVE_PRESENT_6 = ["subjunctive", "present", "5"]

VERB_SUBJUNCTIVE_IMPERFECT_1 = ["subjunctive", "imperfect", "0"]
VERB_SUBJUNCTIVE_IMPERFECT_2 = ["subjunctive", "imperfect", "1"]
VERB_SUBJUNCTIVE_IMPERFECT_3 = ["subjunctive", "imperfect", "2"]
VERB_SUBJUNCTIVE_IMPERFECT_4 = ["subjunctive", "imperfect", "3"]
VERB_SUBJUNCTIVE_IMPERFECT_5 = ["subjunctive", "imperfect", "4"]
VERB_SUBJUNCTIVE_IMPERFECT_6 = ["subjunctive", "imperfect", "5"]

VERB_CONDITIONAL_PRESENT_1 = ["conditional", "present", "0"]
VERB_CONDITIONAL_PRESENT_2 = ["conditional", "present", "1"]
VERB_CONDITIONAL_PRESENT_3 = ["conditional", "present", "2"]
VERB_CONDITIONAL_PRESENT_4 = ["conditional", "present", "3"]
VERB_CONDITIONAL_PRESENT_5 = ["conditional", "present", "4"]
VERB_CONDITIONAL_PRESENT_6 = ["conditional", "present", "5"]

VERB_IMPERATIVE_PRESENT_II_S = ["imperative", "imperative-present", "0"]
VERB_IMPERATIVE_PRESENT_I_P = ["imperative", "imperative-present", "1"]
VERB_IMPERATIVE_PRESENT_II_P = ["imperative", "imperative-present", "2"]

VERB_PRESENT_PARTICIPLE = ["participle", "present-participle", "0"]

VERB_PAST_PARTICIPLE_S_M = ["participle", "past-participle", "0"]
VERB_PAST_PARTICIPLE_S_F = ["participle", "past-participle", "2"]
VERB_PAST_PARTICIPLE_P_M = ["participle", "past-participle", "1"]
VERB_PAST_PARTICIPLE_P_F = ["participle", "past-participle", "3"]
FORMULAS = {
    'indicative': {
        'present': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_PRESENT_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_PRESENT_6,), (("",),),),),
            },
        },
        'composé-past': {
            1: {
                'person_I_S': (((("j'<i>ai</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu <i>as</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il <i>a</i> ",), ("elle <i>a</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous <i>avons</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous <i>avez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils <i>ont</i> ",), ("elles <i>ont</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {

                'person_I_S': (((("je <i>suis</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu <i>es</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il <i>est</i> ",), ("elle <i>est</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous <i>sommes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous <i>êtes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils <i>sont</i> ",), ("elles <i>sont</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
        'imperfect': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_IMPERFECT_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_IMPERFECT_6,), (("",),),),),
            },
        },
        'pluperfect': {
            1: {
                'person_I_S': (((("j'<i>avais</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu <i>avais</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il <i>avait</i> ",), ("elle <i>avait</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous <i>avions</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous <i>aviez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils <i>avaient</i> ",), ("elles <i>avaient</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_I_S': (((("j'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu <i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il <i>était</i> ",), ("elle <i>était</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous <i>étions</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous <i>étiez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils <i>étaient</i> ",), ("elles <i>étaient</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
        'simple-past': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_SIMPLE_PAST_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_SIMPLE_PAST_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_SIMPLE_PAST_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_SIMPLE_PAST_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_SIMPLE_PAST_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_SIMPLE_PAST_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_SIMPLE_PAST_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_SIMPLE_PAST_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_SIMPLE_PAST_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_SIMPLE_PAST_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_SIMPLE_PAST_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_SIMPLE_PAST_6,), (("",),),),),
            }
        },
        'antérieur-past': {
            1: {
                'person_I_S': (((("j'<i>eus</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu <i>eus</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il <i>eut</i> ",), ("elle <i>eut</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous <i>eûmes</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous <i>eûtes</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils <i>eurent</i> ",), ("elles <i>eurent</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il <i>fut</i> ",), ("elle <i>fut</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous <i>fûmes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous <i>fûtes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils <i>furent</i> ",), ("elles <i>furent</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
        'future': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_FUTURE_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_FUTURE_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_FUTURE_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_FUTURE_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_FUTURE_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_FUTURE_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_FUTURE_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_FUTURE_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_FUTURE_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_FUTURE_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_FUTURE_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_FUTURE_6,), (("",),),),),
            }
        },
        'antérieur-future': {
            1: {
                'person_I_S': (((("j'<i>aurai</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu <i>auras</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il <i>aura</i> ",), ("elle <i>aura</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous <i>aurons</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous <i>aurez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils <i>auront</i> ",), ("elles <i>auront</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je <i>serai</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu <i>seras</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il <i>sera</i> ",), ("elle <i>sera</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous <i>serons</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous <i>serez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils <i>seront</i> ",), ("elles <i>seront</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
    },
    'subjunctive': {
        'present': {
            1: {
                'person_I_S': (((("que je ", "que j'",),), (VERB_SUBJUNCTIVE_PRESENT_1,), (("",),),),),
                'person_II_S': (((("que tu ",),), (VERB_SUBJUNCTIVE_PRESENT_2,), (("",),),),),
                'person_III_S': (((("qu'il ",), ("qu'elle ",),), (VERB_SUBJUNCTIVE_PRESENT_3,), (("",),),),),
                'person_I_P': (((("que nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4,), (("",),),),),
                'person_II_P': (((("que vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5,), (("",),),),),
                'person_III_P': (((("qu'ils ",), ("qu'elles ",),), (VERB_SUBJUNCTIVE_PRESENT_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("que je ", "que j'",),), (VERB_SUBJUNCTIVE_PRESENT_1,), (("",),),),),
                'person_II_S': (((("que tu ",),), (VERB_SUBJUNCTIVE_PRESENT_2,), (("",),),),),
                'person_III_S': (((("qu'il ",), ("qu'elle ",),), (VERB_SUBJUNCTIVE_PRESENT_3,), (("",),),),),
                'person_I_P': (((("que nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4,), (("",),),),),
                'person_II_P': (((("que vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5,), (("",),),),),
                'person_III_P': (((("qu'ils ",), ("qu'elles ",),), (VERB_SUBJUNCTIVE_PRESENT_6,), (("",),),),),
            },
        },
        'past': {
            1: {
                'person_I_S': (((("que j'<i>aie</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("que tu <i>aies</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("qu'il <i>ait</i> ",), ("qu'elle <i>ait</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("que nous <i>ayons</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("que vous <i>ayez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("qu'ils <i>aient</i> ",), ("qu'elles <i>aient</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {

                'person_I_S': (((("que je <i>sois</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("que tu <i>sois</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("qu'il <i>soit</i> ",), ("qu'elle <i>soit</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("que nous <i>soyons</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("que vous <i>soyez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("qu'ils <i>soient</i> ",), ("qu'elles <i>soient</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
        'imperfect': {
            1: {
                'person_I_S': (((("que <i>je</i> ", "que j'",),), (VERB_SUBJUNCTIVE_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("que <i>tu</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("qu'<i>il</i> ",), ("qu'<i>elle</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("que <i>nous</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("que <i>vous</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("qu'<i>ils</i> ",), ("qu'<i>elles</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("que <i>je</i> ", "que j'",),), (VERB_SUBJUNCTIVE_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("que <i>tu</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("qu'<i>il</i> ",), ("qu'<i>elle</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("que <i>nous</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("que <i>vous</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("qu'<i>ils</i> ",), ("qu'<i>elles</i> ",),), (VERB_SUBJUNCTIVE_IMPERFECT_6,), (("",),),),),
            },
        },
        'pluperfect': {
            1: {
                'person_I_S': (((("que j'<i>eusse</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("que tu <i>eusses</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("qu'il <i>eût</i> ",), ("qu'elle <i>eût</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("que nous <i>eussions</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("que vous <i>eussiez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("qu'ils <i>eussent</i> ",), ("qu'elles <i>eussent</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_I_S': (((("que je <i>fusse</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("que tu <i>fusses</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("qu'il <i>fût</i> ",), ("qu'elle <i>fût</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("que nous <i>fussions</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("que vous <i>fussiez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("qu'ils <i>fussent</i> ",), ("qu'elles <i>fussent</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
    },
    'conditional': {
        'present': {
            1: {
                'person_I_S': (((("je ", "j'",),), (VERB_CONDITIONAL_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_CONDITIONAL_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_CONDITIONAL_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_CONDITIONAL_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_CONDITIONAL_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_CONDITIONAL_PRESENT_6,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je ", "j'",),), (VERB_CONDITIONAL_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu ",),), (VERB_CONDITIONAL_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il ",), ("elle ",),), (VERB_CONDITIONAL_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous ",),), (VERB_CONDITIONAL_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous ",),), (VERB_CONDITIONAL_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils ",), ("elles ",),), (VERB_CONDITIONAL_PRESENT_6,), (("",),),),),
            }
        },
        'past-first': {
            1: {
                'person_I_S': (((("j'<i>aurais</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu <i>aurais</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il <i>aurait</i> ",), ("elle <i>aurait</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous <i>aurions</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous <i>auriez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils <i>auraient</i> ",), ("elles <i>auraient</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_I_S': (((("je <i>serais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu <i>serais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il <i>serait</i> ",), ("elle <i>serait</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous <i>serions</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous <i>seriez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils <i>seraient</i> ",), ("elles <i>seraient</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
            },
        },
        # 'past-second': {
        #     1: {
        #         'person_I_S': (((("j'<i>eusse</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
        #         'person_II_S': (((("tu <i>eusses</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
        #         'person_III_S': (((("il <i>eût</i> ",), ("elle <i>eût</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
        #         'person_I_P': (((("nous <i>eussions</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
        #         'person_II_P': (((("vous <i>eussiez</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
        #         'person_III_P': (((("ils <i>eussent</i> ",), ("elles <i>eussent</i> ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
        #     },
        #     2: {
        #         'person_I_S': (((("je <i>fusse</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
        #         'person_II_S': (((("tu <i>fusses</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
        #         'person_III_S': (((("il <i>fût</i> ",), ("elle <i>fût</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
        #         'person_I_P': (((("nous <i>fussions</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
        #         'person_II_P': (((("vous <i>fussiez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
        #         'person_III_P': (((("ils <i>fussent</i> ",), ("elles <i>fussent</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
        #     },
        # },
    },
    'imperative': {
        'present': {
            1: {
                'person_II_S': (((("",),), (VERB_IMPERATIVE_PRESENT_II_S,), (("",),),),),
                'person_I_P': (((("",),), (VERB_IMPERATIVE_PRESENT_I_P,), (("",),),),),
                'person_II_P': (((("",),), (VERB_IMPERATIVE_PRESENT_II_P,), (("",),),),),
            },
            2: {
                'person_II_S': (((("",),), (VERB_IMPERATIVE_PRESENT_II_S,), (("",),),),),
                'person_I_P': (((("",),), (VERB_IMPERATIVE_PRESENT_I_P,), (("",),),),),
                'person_II_P': (((("",),), (VERB_IMPERATIVE_PRESENT_II_P,), (("",),),),),
            },
        },
        'past': {
            1: {
                'person_II_S': (((("aie ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("ayons ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("ayez ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_II_S': (((("sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("souons ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("soyez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
        },
    },
    'participle': {
        'present': {
            1: {
                'person_I_S': (((("",),), (VERB_PRESENT_PARTICIPLE,), (("",),),),),  # (TODO person name?,)
            },
            2: {
                'person_I_S': (((("",),), (VERB_PRESENT_PARTICIPLE,), (("",),),),),  # (TODO person name?,)
            },
        },
        'past': {
            1: {
                'person_I_S': (((("",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_S': (((("ayant ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),  # (TODO person name?,)
            },
            2: {
                'person_I_S': (((("",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_S': (((("étant ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),  # (TODO person name?,)
            }
        }
    },
    'infinitive': {
        'present': {
            1: {
                'person_I_S': (((("",),), (VERB_INFINITIVE,), (("",),),),),
            },
            2: {
                'person_I_S': (((("",),), (VERB_INFINITIVE,), (("",),),),),
            },
        },
        'past': {
            1: {
                'person_I_S': (((("avoir ",),), (VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
            },
            2: {
                'person_I_S': (((("être ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
            },
        }
    },
    'gerund': {
        'present': {
            1: {
                'person_I_S': (((("en ",),), (VERB_PRESENT_PARTICIPLE,), (("",),),),),
            },
            2: {
                'person_I_S': (((("en ",),), (VERB_PRESENT_PARTICIPLE,), (("",),),),),
            },
        },
        'past': {
            1: {
                'person_I_S': (((("en <i>ayant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
            },
            2: {
                'person_I_S': (((("en <i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
            },
        },
    }
}

FORMULAS_PASSIVE = {
    'indicative':{
        'present':{
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_PRESENT_1, VERB_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_PRESENT_2, VERB_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_PRESENT_3, VERB_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_PRESENT_4, VERB_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_PRESENT_5, VERB_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_PRESENT_6, VERB_PRESENT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_PRESENT_1, VERB_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_PRESENT_2, VERB_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_PRESENT_3, VERB_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_PRESENT_4, VERB_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_PRESENT_5, VERB_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_PRESENT_6, VERB_PRESENT_6,), (("",),),),)}},
        'composé-past': {
            1: {
                'person_I_S': (((("je me <i>suis</i> ", "je me <i>suis</i> ",), ("je me <i>suis</i> ", "je me <i>suis</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu t'<i>es</i> ", "tu t'<i>es</i> ",), ("tu t'<i>es</i> ", "tu t'<i>es</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il s'<i>est</i> ", "il s'<i>est</i> ",), ("elle s'<i>est</i> ", "elle s'<i>est</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",), ("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",), ("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se <i>sont</i> ", "ils se <i>sont</i> ",), ("elles se <i>sont</i> ", "elles se <i>sont</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("je me <i>suis</i> ", "je me <i>suis</i> ",), ("je me <i>suis</i> ", "je me <i>suis</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu t'<i>es</i> ", "tu t'<i>es</i> ",), ("tu t'<i>es</i> ", "tu t'<i>es</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il s'<i>est</i> ", "il s'<i>est</i> ",), ("elle s'<i>est</i> ", "elle s'<i>est</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",), ("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",), ("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se <i>sont</i> ", "ils se <i>sont</i> ",), ("elles se <i>sont</i> ", "elles se <i>sont</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}},
        'imperfect': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_IMPERFECT_1, VERB_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_IMPERFECT_2, VERB_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_IMPERFECT_3, VERB_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_IMPERFECT_4, VERB_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_IMPERFECT_5, VERB_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_IMPERFECT_6, VERB_IMPERFECT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_IMPERFECT_1, VERB_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_IMPERFECT_2, VERB_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_IMPERFECT_3, VERB_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_IMPERFECT_4, VERB_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_IMPERFECT_5, VERB_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_IMPERFECT_6, VERB_IMPERFECT_6,), (("",),),),)}},
        'pluperfect': {
            1: {
                'person_I_S': (((("je m'<i>étais</i> ", "je m'<i>étais</i> ",), ("je m'<i>étais</i> ", "je m'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",), ("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il s'<i>était</i> ", "il s'<i>était</i> ",), ("elle s'<i>était</i> ", "elle s'<i>était</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",), ("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",), ("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils s'<i>étaient</i> ", "ils s'<i>étaient</i> ",), ("elles s'<i>étaient</i> ", "elles s'<i>étaient</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("je m'<i>étais</i> ", "je m'<i>étais</i> ",), ("je m'<i>étais</i> ", "je m'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",), ("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il s'<i>était</i> ", "il s'<i>était</i> ",), ("elle s'<i>était</i> ", "elle s'<i>était</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",), ("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",), ("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils s'<i>étaient</i> ", "ils s'<i>étaient</i> ",), ("elles s'<i>étaient</i> ", "elles s'<i>étaient</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}},
        'simple-past': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_SIMPLE_PAST_1, VERB_SIMPLE_PAST_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_SIMPLE_PAST_2, VERB_SIMPLE_PAST_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_SIMPLE_PAST_3, VERB_SIMPLE_PAST_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_SIMPLE_PAST_4, VERB_SIMPLE_PAST_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_SIMPLE_PAST_5, VERB_SIMPLE_PAST_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_SIMPLE_PAST_6, VERB_SIMPLE_PAST_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_SIMPLE_PAST_1, VERB_SIMPLE_PAST_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_SIMPLE_PAST_2, VERB_SIMPLE_PAST_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_SIMPLE_PAST_3, VERB_SIMPLE_PAST_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_SIMPLE_PAST_4, VERB_SIMPLE_PAST_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_SIMPLE_PAST_5, VERB_SIMPLE_PAST_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_SIMPLE_PAST_6, VERB_SIMPLE_PAST_6,), (("",),),),)}},
        'antérieur-past': {
            1: {
                'person_I_S': (((("je me <i>fus</i> ", "je me <i>fus</i> ",), ("je me <i>fus</i> ", "je me <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu te <i>fus</i> ", "tu te <i>fus</i> ",), ("tu te <i>fus</i> ", "tu te <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il se <i>fut</i> ", "il se <i>fut</i> ",), ("elle se <i>fut</i> ", "elle se <i>fut</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",), ("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",), ("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se <i>furent</i> ", "ils se <i>furent</i> ",), ("elles se <i>furent</i> ", "elles se <i>furent</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("je me <i>fus</i> ", "je me <i>fus</i> ",), ("je me <i>fus</i> ", "je me <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu te <i>fus</i> ", "tu te <i>fus</i> ",), ("tu te <i>fus</i> ", "tu te <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il se <i>fut</i> ", "il se <i>fut</i> ",), ("elle se <i>fut</i> ", "elle se <i>fut</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",), ("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",), ("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se <i>furent</i> ", "ils se <i>furent</i> ",), ("elles se <i>furent</i> ", "elles se <i>furent</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}},
        'future': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_FUTURE_1, VERB_FUTURE_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_FUTURE_2, VERB_FUTURE_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_FUTURE_3, VERB_FUTURE_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_FUTURE_4, VERB_FUTURE_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_FUTURE_5, VERB_FUTURE_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_FUTURE_6, VERB_FUTURE_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_FUTURE_1, VERB_FUTURE_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_FUTURE_2, VERB_FUTURE_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_FUTURE_3, VERB_FUTURE_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_FUTURE_4, VERB_FUTURE_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_FUTURE_5, VERB_FUTURE_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_FUTURE_6, VERB_FUTURE_6,), (("",),),),)}},
        'antérieur-future': {
            1: {
                'person_I_S': (((("je me <i>serai</i> ", "je me <i>serai</i> ",), ("je me <i>serai</i> ", "je me <i>serai</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu te <i>seras</i> ", "tu te <i>seras</i> ",), ("tu te <i>seras</i> ", "tu te <i>seras</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il se <i>sera</i> ", "il se <i>sera</i> ",), ("elle se <i>sera</i> ", "elle se <i>sera</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",), ("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",), ("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se <i>seront</i> ", "ils se <i>seront</i> ",), ("elles se <i>seront</i> ", "elles se <i>seront</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("je me <i>serai</i> ", "je me <i>serai</i> ",), ("je me <i>serai</i> ", "je me <i>serai</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu te <i>seras</i> ", "tu te <i>seras</i> ",), ("tu te <i>seras</i> ", "tu te <i>seras</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il se <i>sera</i> ", "il se <i>sera</i> ",), ("elle se <i>sera</i> ", "elle se <i>sera</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",), ("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",), ("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se <i>seront</i> ", "ils se <i>seront</i> ",), ("elles se <i>seront</i> ", "elles se <i>seront</i> ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}}},
    'subjunctive': {
        'present': {
            1: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_PRESENT_1, VERB_SUBJUNCTIVE_PRESENT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_PRESENT_2, VERB_SUBJUNCTIVE_PRESENT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_PRESENT_3, VERB_SUBJUNCTIVE_PRESENT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4, VERB_SUBJUNCTIVE_PRESENT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5, VERB_SUBJUNCTIVE_PRESENT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_PRESENT_6, VERB_SUBJUNCTIVE_PRESENT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_PRESENT_1, VERB_SUBJUNCTIVE_PRESENT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_PRESENT_2, VERB_SUBJUNCTIVE_PRESENT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_PRESENT_3, VERB_SUBJUNCTIVE_PRESENT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4, VERB_SUBJUNCTIVE_PRESENT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5, VERB_SUBJUNCTIVE_PRESENT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_PRESENT_6, VERB_SUBJUNCTIVE_PRESENT_6,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': (((("que je me sois ", "que je me sois ",), ("que je me sois ", "que je me sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("que tu te sois ", "que tu te sois ",), ("que tu te sois ", "que tu te sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("qu'il se soit ", "qu'il se soit ",), ("qu'elle se soit ", "qu'elle se soit ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("que nous nous soyons ", "que nous nous soyons ",), ("que nous nous soyons ", "que nous nous soyons ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("que vous vous soyez ", "que vous vous soyez ",), ("que vous vous soyez ", "que vous vous soyez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("qu'ils se soient ", "qu'ils se soient ",), ("qu'elles se soient ", "qu'elles se soient ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me sois ", "que je me sois ",), ("que je me sois ", "que je me sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("que tu te sois ", "que tu te sois ",), ("que tu te sois ", "que tu te sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("qu'il se soit ", "qu'il se soit ",), ("qu'elle se soit ", "qu'elle se soit ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("que nous nous soyons ", "que nous nous soyons ",), ("que nous nous soyons ", "que nous nous soyons ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("que vous vous soyez ", "que vous vous soyez ",), ("que vous vous soyez ", "que vous vous soyez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("qu'ils se soient ", "qu'ils se soient ",), ("qu'elles se soient ", "qu'elles se soient ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}},
        'imperfect': {
            1: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_IMPERFECT_1, VERB_SUBJUNCTIVE_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2, VERB_SUBJUNCTIVE_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_3, VERB_SUBJUNCTIVE_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4, VERB_SUBJUNCTIVE_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5, VERB_SUBJUNCTIVE_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_6, VERB_SUBJUNCTIVE_IMPERFECT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_IMPERFECT_1, VERB_SUBJUNCTIVE_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2, VERB_SUBJUNCTIVE_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_3, VERB_SUBJUNCTIVE_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4, VERB_SUBJUNCTIVE_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5, VERB_SUBJUNCTIVE_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_6, VERB_SUBJUNCTIVE_IMPERFECT_6,), (("",),),),)}},
        'pluperfect': {
            1: {
                'person_I_S': (((("que je me fusse ", "que je me fusse ",), ("que je me fusse ", "que je me fusse ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("que tu te fusses ", "que tu te fusses ",), ("que tu te fusses ", "que tu te fusses ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("qu'il se fût ", "qu'il se fût ",), ("qu'elle se fût ", "qu'elle se fût ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("que nous nous fussions ", "que nous nous fussions ",), ("que nous nous fussions ", "que nous nous fussions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("que vous vous fussiez ", "que vous vous fussiez ",), ("que vous vous fussiez ", "que vous vous fussiez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("qu'ils se fussent ", "qu'ils se fussent ",), ("qu'elles se fussent ", "qu'elles se fussent ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me fusse ", "que je me fusse ",), ("que je me fusse ", "que je me fusse ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("que tu te fusses ", "que tu te fusses ",), ("que tu te fusses ", "que tu te fusses ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("qu'il se fût ", "qu'il se fût ",), ("qu'elle se fût ", "qu'elle se fût ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("que nous nous fussions ", "que nous nous fussions ",), ("que nous nous fussions ", "que nous nous fussions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("que vous vous fussiez ", "que vous vous fussiez ",), ("que vous vous fussiez ", "que vous vous fussiez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("qu'ils se fussent ", "qu'ils se fussent ",), ("qu'elles se fussent ", "qu'elles se fussent ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}}},
    'conditional': {
        'present': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_CONDITIONAL_PRESENT_1, VERB_CONDITIONAL_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_CONDITIONAL_PRESENT_2, VERB_CONDITIONAL_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_CONDITIONAL_PRESENT_3, VERB_CONDITIONAL_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_CONDITIONAL_PRESENT_4, VERB_CONDITIONAL_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_CONDITIONAL_PRESENT_5, VERB_CONDITIONAL_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_CONDITIONAL_PRESENT_6, VERB_CONDITIONAL_PRESENT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_CONDITIONAL_PRESENT_1, VERB_CONDITIONAL_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_CONDITIONAL_PRESENT_2, VERB_CONDITIONAL_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_CONDITIONAL_PRESENT_3, VERB_CONDITIONAL_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_CONDITIONAL_PRESENT_4, VERB_CONDITIONAL_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_CONDITIONAL_PRESENT_5, VERB_CONDITIONAL_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_CONDITIONAL_PRESENT_6, VERB_CONDITIONAL_PRESENT_6,), (("",),),),)}},
        'past-first': {
            1: {
                'person_I_S': (((("je me serais ", "je me serais ",), ("je me serais ", "je me serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu te serais ", "tu te serais ",), ("tu te serais ", "tu te serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il se serait ", "il se serait ",), ("elle se serait ", "elle se serait ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous serions ", "nous nous serions ",), ("nous nous serions ", "nous nous serions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous seriez ", "vous vous seriez ",), ("vous vous seriez ", "vous vous seriez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se seraient ", "ils se seraient ",), ("elles se seraient ", "elles se seraient ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)},
            2: {
                'person_I_S': (((("je me serais ", "je me serais ",), ("je me serais ", "je me serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_II_S': (((("tu te serais ", "tu te serais ",), ("tu te serais ", "tu te serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_III_S': (((("il se serait ", "il se serait ",), ("elle se serait ", "elle se serait ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': (((("nous nous serions ", "nous nous serions ",), ("nous nous serions ", "nous nous serions ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_P': (((("vous vous seriez ", "vous vous seriez ",), ("vous vous seriez ", "vous vous seriez ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_III_P': (((("ils se seraient ", "ils se seraient ",), ("elles se seraient ", "elles se seraient ",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),)}},
            },
    'imperative': {
        'present': {
            1: {
                'person_II_S': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_S, VERB_IMPERATIVE_PRESENT_II_S,), (("-toi ",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_I_P, VERB_IMPERATIVE_PRESENT_I_P,), (("-nous ",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_P, VERB_IMPERATIVE_PRESENT_II_P,), (("-vous ",),),),)},
            2: {
                'person_II_S': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_S, VERB_IMPERATIVE_PRESENT_II_S,), (("-toi ",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_I_P, VERB_IMPERATIVE_PRESENT_I_P,), (("-nous ",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_P, VERB_IMPERATIVE_PRESENT_II_P,), (("-vous ",),),),)}},
        'past': {
            1: {
                'person_II_S': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),)},
            2: {
                'person_II_S': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),)}}},
    'participle': {
        'present': {
            1: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)},
            2: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_S': (((("s'<i>étant</i> ", "s'<i>étant</i> ",), ("s'<i>étant</i> ", "s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),)},
            2: {
                'person_I_S': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_S': (((("s'<i>étant</i> ", "s'<i>étant</i> ",), ("s'<i>étant</i> ", "s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),)}}},
    'infinitive': {
        'present': {
            1: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_INFINITIVE, VERB_INFINITIVE,), (("",),),),)},
            2: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_INFINITIVE, VERB_INFINITIVE,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': (((("s'<i>être</i> ", "s'<i>être</i> ",), ("s'<i>être</i> ", "s'<i>être</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("s'<i>être</i> ", "s'<i>être</i> ",), ("s'<i>être</i> ", "s'<i>être</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}}},
    'gerund': {
        'present': {
            1: {
                'person_I_S': (((("en se ", "en s'",), ("en se ", "en se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)},
            2: {
                'person_I_S': (((("en se ", "en s'",), ("en se ", "en se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': (((("en s'<i>étant</i> ", "en s'<i>étant</i> ",), ("en s'<i>étant</i> ", "en s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("en s'<i>étant</i> ", "en s'<i>étant</i> ",), ("en s'<i>étant</i> ", "en s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}}}}

FORMULAS_PASSIVE_X = {
    'indicative':{
        'present':{
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_PRESENT_1, VERB_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_PRESENT_2, VERB_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_PRESENT_3, VERB_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_PRESENT_4, VERB_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_PRESENT_5, VERB_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_PRESENT_6, VERB_PRESENT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_PRESENT_1, VERB_PRESENT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_PRESENT_2, VERB_PRESENT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_PRESENT_3, VERB_PRESENT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_PRESENT_4, VERB_PRESENT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_PRESENT_5, VERB_PRESENT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_PRESENT_6, VERB_PRESENT_6,), (("",),),),)}},
        'composé-past': {
            1: {
                'person_I_S': (((("je me <i>suis</i> ", "je me <i>suis</i> ",), ("je me <i>suis</i> ", "je me <i>suis</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu t'<i>es</i> ", "tu t'<i>es</i> ",), ("tu t'<i>es</i> ", "tu t'<i>es</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il s'<i>est</i> ", "il s'<i>est</i> ",), ("elle s'<i>est</i> ", "elle s'<i>est</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",), ("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",), ("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se <i>sont</i> ", "ils se <i>sont</i> ",), ("elles se <i>sont</i> ", "elles se <i>sont</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("je me <i>suis</i> ", "je me <i>suis</i> ",), ("je me <i>suis</i> ", "je me <i>suis</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu t'<i>es</i> ", "tu t'<i>es</i> ",), ("tu t'<i>es</i> ", "tu t'<i>es</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il s'<i>est</i> ", "il s'<i>est</i> ",), ("elle s'<i>est</i> ", "elle s'<i>est</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",), ("nous nous <i>sommes</i> ", "nous nous <i>sommes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",), ("vous vous <i>êtes</i> ", "vous vous <i>êtes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se <i>sont</i> ", "ils se <i>sont</i> ",), ("elles se <i>sont</i> ", "elles se <i>sont</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}},
        'imperfect': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_IMPERFECT_1, VERB_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_IMPERFECT_2, VERB_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_IMPERFECT_3, VERB_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_IMPERFECT_4, VERB_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_IMPERFECT_5, VERB_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_IMPERFECT_6, VERB_IMPERFECT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_IMPERFECT_1, VERB_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_IMPERFECT_2, VERB_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_IMPERFECT_3, VERB_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_IMPERFECT_4, VERB_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_IMPERFECT_5, VERB_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_IMPERFECT_6, VERB_IMPERFECT_6,), (("",),),),)}},
        'pluperfect': {
            1: {
                'person_I_S': (((("je m'<i>étais</i> ", "je m'<i>étais</i> ",), ("je m'<i>étais</i> ", "je m'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",), ("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il s'<i>était</i> ", "il s'<i>était</i> ",), ("elle s'<i>était</i> ", "elle s'<i>était</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",), ("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",), ("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils s'<i>étaient</i> ", "ils s'<i>étaient</i> ",), ("elles s'<i>étaient</i> ", "elles s'<i>étaient</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("je m'<i>étais</i> ", "je m'<i>étais</i> ",), ("je m'<i>étais</i> ", "je m'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",), ("tu t'<i>étais</i> ", "tu t'<i>étais</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il s'<i>était</i> ", "il s'<i>était</i> ",), ("elle s'<i>était</i> ", "elle s'<i>était</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",), ("nous nous <i>étions</i> ", "nous nous <i>étions</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",), ("vous vous <i>étiez</i> ", "vous vous <i>étiez</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils s'<i>étaient</i> ", "ils s'<i>étaient</i> ",), ("elles s'<i>étaient</i> ", "elles s'<i>étaient</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}},
        'simple-past': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_SIMPLE_PAST_1, VERB_SIMPLE_PAST_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_SIMPLE_PAST_2, VERB_SIMPLE_PAST_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_SIMPLE_PAST_3, VERB_SIMPLE_PAST_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_SIMPLE_PAST_4, VERB_SIMPLE_PAST_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_SIMPLE_PAST_5, VERB_SIMPLE_PAST_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_SIMPLE_PAST_6, VERB_SIMPLE_PAST_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_SIMPLE_PAST_1, VERB_SIMPLE_PAST_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_SIMPLE_PAST_2, VERB_SIMPLE_PAST_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_SIMPLE_PAST_3, VERB_SIMPLE_PAST_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_SIMPLE_PAST_4, VERB_SIMPLE_PAST_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_SIMPLE_PAST_5, VERB_SIMPLE_PAST_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_SIMPLE_PAST_6, VERB_SIMPLE_PAST_6,), (("",),),),)}},
        'antérieur-past': {
            1: {
                'person_I_S': (((("je me <i>fus</i> ", "je me <i>fus</i> ",), ("je me <i>fus</i> ", "je me <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu te <i>fus</i> ", "tu te <i>fus</i> ",), ("tu te <i>fus</i> ", "tu te <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il se <i>fut</i> ", "il se <i>fut</i> ",), ("elle se <i>fut</i> ", "elle se <i>fut</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",), ("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",), ("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se <i>furent</i> ", "ils se <i>furent</i> ",), ("elles se <i>furent</i> ", "elles se <i>furent</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("je me <i>fus</i> ", "je me <i>fus</i> ",), ("je me <i>fus</i> ", "je me <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu te <i>fus</i> ", "tu te <i>fus</i> ",), ("tu te <i>fus</i> ", "tu te <i>fus</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il se <i>fut</i> ", "il se <i>fut</i> ",), ("elle se <i>fut</i> ", "elle se <i>fut</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",), ("nous nous <i>fûmes</i> ", "nous nous <i>fûmes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",), ("vous vous <i>fûtes</i> ", "vous vous <i>fûtes</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se <i>furent</i> ", "ils se <i>furent</i> ",), ("elles se <i>furent</i> ", "elles se <i>furent</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}},
        'future': {
            1: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_FUTURE_1, VERB_FUTURE_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_FUTURE_2, VERB_FUTURE_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_FUTURE_3, VERB_FUTURE_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_FUTURE_4, VERB_FUTURE_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_FUTURE_5, VERB_FUTURE_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_FUTURE_6, VERB_FUTURE_6,), (("",),),),)},
            2: {
                'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_FUTURE_1, VERB_FUTURE_1,), (("",),),),),
                'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_FUTURE_2, VERB_FUTURE_2,), (("",),),),),
                'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_FUTURE_3, VERB_FUTURE_3,), (("",),),),),
                'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_FUTURE_4, VERB_FUTURE_4,), (("",),),),),
                'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_FUTURE_5, VERB_FUTURE_5,), (("",),),),),
                'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_FUTURE_6, VERB_FUTURE_6,), (("",),),),)}},
        'antérieur-future': {
            1: {
                'person_I_S': (((("je me <i>serai</i> ", "je me <i>serai</i> ",), ("je me <i>serai</i> ", "je me <i>serai</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu te <i>seras</i> ", "tu te <i>seras</i> ",), ("tu te <i>seras</i> ", "tu te <i>seras</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il se <i>sera</i> ", "il se <i>sera</i> ",), ("elle se <i>sera</i> ", "elle se <i>sera</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",), ("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",), ("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se <i>seront</i> ", "ils se <i>seront</i> ",), ("elles se <i>seront</i> ", "elles se <i>seront</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("je me <i>serai</i> ", "je me <i>serai</i> ",), ("je me <i>serai</i> ", "je me <i>serai</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu te <i>seras</i> ", "tu te <i>seras</i> ",), ("tu te <i>seras</i> ", "tu te <i>seras</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il se <i>sera</i> ", "il se <i>sera</i> ",), ("elle se <i>sera</i> ", "elle se <i>sera</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",), ("nous nous <i>serons</i> ", "nous nous <i>serons</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",), ("vous vous <i>serez</i> ", "vous vous <i>serez</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se <i>seront</i> ", "ils se <i>seront</i> ",), ("elles se <i>seront</i> ", "elles se <i>seront</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}}},
    'subjunctive': {
        'present': {
            1: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_PRESENT_1, VERB_SUBJUNCTIVE_PRESENT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_PRESENT_2, VERB_SUBJUNCTIVE_PRESENT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_PRESENT_3, VERB_SUBJUNCTIVE_PRESENT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4, VERB_SUBJUNCTIVE_PRESENT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5, VERB_SUBJUNCTIVE_PRESENT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_PRESENT_6, VERB_SUBJUNCTIVE_PRESENT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_PRESENT_1, VERB_SUBJUNCTIVE_PRESENT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_PRESENT_2, VERB_SUBJUNCTIVE_PRESENT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_PRESENT_3, VERB_SUBJUNCTIVE_PRESENT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_PRESENT_4, VERB_SUBJUNCTIVE_PRESENT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_PRESENT_5, VERB_SUBJUNCTIVE_PRESENT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_PRESENT_6, VERB_SUBJUNCTIVE_PRESENT_6,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': (((("que je me sois ", "que je me sois ",), ("que je me sois ", "que je me sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("que tu te sois ", "que tu te sois ",), ("que tu te sois ", "que tu te sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("qu'il se soit ", "qu'il se soit ",), ("qu'elle se soit ", "qu'elle se soit ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("que nous nous soyons ", "que nous nous soyons ",), ("que nous nous soyons ", "que nous nous soyons ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("que vous vous soyez ", "que vous vous soyez ",), ("que vous vous soyez ", "que vous vous soyez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("qu'ils se soient ", "qu'ils se soient ",), ("qu'elles se soient ", "qu'elles se soient ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me sois ", "que je me sois ",), ("que je me sois ", "que je me sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("que tu te sois ", "que tu te sois ",), ("que tu te sois ", "que tu te sois ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("qu'il se soit ", "qu'il se soit ",), ("qu'elle se soit ", "qu'elle se soit ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("que nous nous soyons ", "que nous nous soyons ",), ("que nous nous soyons ", "que nous nous soyons ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("que vous vous soyez ", "que vous vous soyez ",), ("que vous vous soyez ", "que vous vous soyez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("qu'ils se soient ", "qu'ils se soient ",), ("qu'elles se soient ", "qu'elles se soient ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}},
        'imperfect': {
            1: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_IMPERFECT_1, VERB_SUBJUNCTIVE_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2, VERB_SUBJUNCTIVE_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se '", "qu'elle s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_3, VERB_SUBJUNCTIVE_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4, VERB_SUBJUNCTIVE_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5, VERB_SUBJUNCTIVE_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_6, VERB_SUBJUNCTIVE_IMPERFECT_6,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me ", "que je m'",), ("que je me ", "que je me ",),), (VERB_SUBJUNCTIVE_IMPERFECT_1, VERB_SUBJUNCTIVE_IMPERFECT_1,), (("",),),),),
                'person_II_S': (((("que tu te ", "que tu t'",), ("que tu te ", "que tu te ",),), (VERB_SUBJUNCTIVE_IMPERFECT_2, VERB_SUBJUNCTIVE_IMPERFECT_2,), (("",),),),),
                'person_III_S': (((("qu'il se ", "qu'il s'",), ("qu'elle se ", "qu'elle s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_3, VERB_SUBJUNCTIVE_IMPERFECT_3,), (("",),),),),
                'person_I_P': (((("que nous nous ", "que nous nous ",), ("que nous nous ", "que nous nous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_4, VERB_SUBJUNCTIVE_IMPERFECT_4,), (("",),),),),
                'person_II_P': (((("que vous vous ", "que vous vous ",), ("que vous vous ", "que vous vous ",),), (VERB_SUBJUNCTIVE_IMPERFECT_5, VERB_SUBJUNCTIVE_IMPERFECT_5,), (("",),),),),
                'person_III_P': (((("qu'ils se ", "qu'ils s'",), ("qu'elles se ", "qu'elles s'",),), (VERB_SUBJUNCTIVE_IMPERFECT_6, VERB_SUBJUNCTIVE_IMPERFECT_6,), (("",),),),)}},
        'pluperfect': {
            1: {
                'person_I_S': (((("que je me fusse ", "que je me fusse ",), ("que je me fusse ", "que je me fusse ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("que tu te fusses ", "que tu te fusses ",), ("que tu te fusses ", "que tu te fusses ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("qu'il se fût ", "qu'il se fût ",), ("qu'elle se fût ", "qu'elle se fût ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("que nous nous fussions ", "que nous nous fussions ",), ("que nous nous fussions ", "que nous nous fussions ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("que vous vous fussiez ", "que vous vous fussiez ",), ("que vous vous fussiez ", "que vous vous fussiez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("qu'ils se fussent ", "qu'ils se fussent ",), ("qu'elles se fussent ", "qu'elles se fussent ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("que je me fusse ", "que je me fusse ",), ("que je me fusse ", "que je me fusse ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("que tu te fusses ", "que tu te fusses ",), ("que tu te fusses ", "que tu te fusses ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("qu'il se fût ", "qu'il se fût ",), ("qu'elle se fût ", "qu'elle se fût ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("que nous nous fussions ", "que nous nous fussions ",), ("que nous nous fussions ", "que nous nous fussions ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("que vous vous fussiez ", "que vous vous fussiez ",), ("que vous vous fussiez ", "que vous vous fussiez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("qu'ils se fussent ", "qu'ils se fussent ",), ("qu'elles se fussent ", "qu'elles se fussent ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}}},
    'conditional': {
        'present': {1: {'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_CONDITIONAL_PRESENT_1, VERB_CONDITIONAL_PRESENT_1,), (("",),),),),
                        'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_CONDITIONAL_PRESENT_2, VERB_CONDITIONAL_PRESENT_2,), (("",),),),),
                        'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_CONDITIONAL_PRESENT_3, VERB_CONDITIONAL_PRESENT_3,), (("",),),),),
                        'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_CONDITIONAL_PRESENT_4, VERB_CONDITIONAL_PRESENT_4,), (("",),),),),
                        'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_CONDITIONAL_PRESENT_5, VERB_CONDITIONAL_PRESENT_5,), (("",),),),),
                        'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_CONDITIONAL_PRESENT_6, VERB_CONDITIONAL_PRESENT_6,), (("",),),),)},
                    2: {
                        'person_I_S': (((("je me ", "je m'",), ("je me ", "je me ",),), (VERB_CONDITIONAL_PRESENT_1, VERB_CONDITIONAL_PRESENT_1,), (("",),),),),
                        'person_II_S': (((("tu te ", "tu t'",), ("tu te ", "tu te ",),), (VERB_CONDITIONAL_PRESENT_2, VERB_CONDITIONAL_PRESENT_2,), (("",),),),),
                        'person_III_S': (((("il se ", "il s'",), ("elle se ", "elle s'",),), (VERB_CONDITIONAL_PRESENT_3, VERB_CONDITIONAL_PRESENT_3,), (("",),),),),
                        'person_I_P': (((("nous nous ", "nous nous ",), ("nous nous ", "nous nous ",),), (VERB_CONDITIONAL_PRESENT_4, VERB_CONDITIONAL_PRESENT_4,), (("",),),),),
                        'person_II_P': (((("vous vous ", "vous vous ",), ("vous vous ", "vous vous ",),), (VERB_CONDITIONAL_PRESENT_5, VERB_CONDITIONAL_PRESENT_5,), (("",),),),),
                        'person_III_P': (((("ils se ", "ils s'",), ("elles se ", "elles s'",),), (VERB_CONDITIONAL_PRESENT_6, VERB_CONDITIONAL_PRESENT_6,), (("",),),),)}},
        'past-first': {
            1: {
                'person_I_S': (((("je me serais ", "je me serais ",), ("je me serais ", "je me serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu te serais ", "tu te serais ",), ("tu te serais ", "tu te serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il se serait ", "il se serait ",), ("elle se serait ", "elle se serait ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous serions ", "nous nous serions ",), ("nous nous serions ", "nous nous serions ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous seriez ", "vous vous seriez ",), ("vous vous seriez ", "vous vous seriez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se seraient ", "ils se seraient ",), ("elles se seraient ", "elles se seraient ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("je me serais ", "je me serais ",), ("je me serais ", "je me serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_S': (((("tu te serais ", "tu te serais ",), ("tu te serais ", "tu te serais ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_S': (((("il se serait ", "il se serait ",), ("elle se serait ", "elle se serait ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_I_P': (((("nous nous serions ", "nous nous serions ",), ("nous nous serions ", "nous nous serions ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_II_P': (((("vous vous seriez ", "vous vous seriez ",), ("vous vous seriez ", "vous vous seriez ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),),
                'person_III_P': (((("ils se seraient ", "ils se seraient ",), ("elles se seraient ", "elles se seraient ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}},
},
    'imperative': {
        'present': {
            1: {
                'person_II_S': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_S, VERB_IMPERATIVE_PRESENT_II_S,), (("-toi ",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_I_P, VERB_IMPERATIVE_PRESENT_I_P,), (("-nous ",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_P, VERB_IMPERATIVE_PRESENT_II_P,), (("-vous ",),),),)},
            2: {
                'person_II_S': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_S, VERB_IMPERATIVE_PRESENT_II_S,), (("-toi ",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_I_P, VERB_IMPERATIVE_PRESENT_I_P,), (("-nous ",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (VERB_IMPERATIVE_PRESENT_II_P, VERB_IMPERATIVE_PRESENT_II_P,), (("-vous ",),),),)}},
        'past': {
            1: {
                'person_II_S': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),)},
            2: {
                'person_II_S': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),),
                'person_II_P': ((((" ", "",), (" ", "",),), (None, None,), (("",),),),)}}},
    'participle': {
        'present': {
            1: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)},
            2: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_S': (((("s'<i>étant</i> ", "s'<i>étant</i> ",), ("s'<i>étant</i> ", "s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),)},
            2: {
                'person_I_S': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),),
                'person_I_P': ((((" ", "",), (" ", "",),), (VERB_PAST_PARTICIPLE_P_M, VERB_PAST_PARTICIPLE_P_F,), (("",),),),),
                'person_II_S': (((("s'<i>étant</i> ", "s'<i>étant</i> ",), ("s'<i>étant</i> ", "s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_F,), (("",),),),)}}},
    'infinitive': {
        'present': {
            1: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_INFINITIVE, VERB_INFINITIVE,), (("",),),),)},
            2: {
                'person_I_S': (((("se ", "s'",), ("se ", "se ",),), (VERB_INFINITIVE, VERB_INFINITIVE,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': (((("s'<i>être</i> ", "s'<i>être</i> ",), ("s'<i>être</i> ", "s'<i>être</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("s'<i>être</i> ", "s'<i>être</i> ",), ("s'<i>être</i> ", "s'<i>être</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}}},
    'gerund': {
        'present': {
            1: {
                'person_I_S': (((("en se ", "en s'",), ("en se ", "en se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)},
            2: {
                'person_I_S': (((("en se ", "en s'",), ("en se ", "en se ",),), (VERB_PRESENT_PARTICIPLE, VERB_PRESENT_PARTICIPLE,), (("",),),),)}},
        'past': {
            1: {
                'person_I_S': (((("en s'<i>étant</i> ", "en s'<i>étant</i> ",), ("en s'<i>étant</i> ", "en s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)},
            2: {
                'person_I_S': (((("en s'<i>étant</i> ", "en s'<i>étant</i> ",), ("en s'<i>étant</i> ", "en s'<i>étant</i> ",),), (VERB_PAST_PARTICIPLE_S_M, VERB_PAST_PARTICIPLE_S_M,), (("",),),),)}}}}


TEMPLATE_NAME = {
    'indicative': "Indicatif",
    'present': "Présent",
    'imperfect': "Imparfait",
    'simple-past': "Passé simple",
    'future': "Futur simple",
    'composé-past': "Passé composé",
    'pluperfect': "Plus que parfait",
    'antérieur-past': "Passé antérieur",
    'antérieur-future': "Futur antérieur",
    'subjunctive': "Subjonctif",
    'past': "Passé",
    'conditional': "Conditionnel",
    'past-first': "Passé",
    'past-second': "Passé deuxième forme",
    'imperative': "Impératif",
    'infinitive': "Infinitif",
    'gerund': "Gérondif",
    'participle':"Participe",
}

SHORT_LIST = {
    'indicative':["simple-past","antérieur-past"],
    'subjunctive':["imperfect","pluperfect"],
    'conditional':["past-second"],
    'imperative':["past"],
    'gerund':[],
    'infinitive':[],
    'participle':[],
}

AUDIO_LIST = ["être",
                     "avoir",
                     "faire",
                     "dire",
                     "pouvoir",
                     "aller",
                     "voir",
                     "vouloir",
                     "venir",
                     "devoir",
                     "prendre",
                     "trouver",
                     "donner",
                     "falloir",
                     "parler",
                     "mettre",
                     "savoir",
                     "passer",
                     "regarder",
                     "aimer",
                     "croire",
                     "demander",
                     "rester",
                     "répondre",
                     "entendre",
                     "penser",
                     "arriver",
                     "connaître",
                     "devenir",
                     "sentir",
                     "sembler",
                     "tenir",
                     "comprendre",
                     "rendre",
                     "attendre",
                     "sortir",
                     "vivre",
                     "reprendre",
                     "entrer",
                     "porter",
                     "chercher",
                     "revenir",
                     "appeler",
                     "mourir",
                     "partir",
                     "jeter",
                     "suivre",
                     "écrire",
                     "montrer",
                     "tomber",
                     "ouvrir",
                     "arrêter",
                     "perdre",
                     "commencer",
                     "paraître",
                     "marcher",
                     "lever",
                     "permettre",
                     "asseoir",
                     "écouter",
                     "monter",
                     "apercevoir",
                     "recevoir",
                     "servir",
                     "finir",
                     "rire",
                     "crier",
                     "jouer",
                     "tourner",
                     "garder",
                     "reconnaître",
                     "quitter",
                     "manger",
                     "courir",
                     "continuer",
                     "oublier",
                     "descendre",
                     "cacher",
                     "poser",
                     "tirer",
                     "présenter",
                     "ajouter",
                     "agir",
                     "retrouver",
                     "offrir",
                     "apprendre",
                     "tuer",
                     "retourner",
                     "rencontrer",
                     "envoyer",
                     "dormir",
                     "pousser",
                     "rappeler",
                     "lire",
                     "changer",
                     "compter",
                     "occuper",
                     "frapper",
                     "travailler",
                     "expliquer",
                     "obtenir",
                     "rentrer",
                     "pleurer",
                     "essayer",
                     "répéter",
                     "payer",
                     "apporter",
                     "boire",
                     "sourire",
                     "coucher",
                     "causer",
                     "exister",
                     "raconter",
                     "serrer",
                     "songer",
                     "manquer",
                     "nommer",
                     "conduire",
                     "saisir",
                     "demeurer",
                     "remettre",
                     "disparaître",
                     "battre",
                     "toucher",
                     "apparaître",
                     "souffrir",
                     "fermer",
                     "accepter",
                     "tendre",
                     "naître",
                     "sauver",
                     "avancer",
                     "traverser",
                     "souvenir",
                     "couvrir",
                     "gagner",
                     "former",
                     "plaire",
                     "embrasser",
                     "oser",
                     "refuser",
                     "décider",
                     "produire",
                     "charger",
                     "mêler",
                     "cesser",
                     "ressembler",
                     "chanter",
                     "empêcher",
                     "approcher",
                     "prier",
                     "espérer",
                     "échapper",
                     "glisser",
                     "briller",
                     "brûler",
                     "placer",
                     "juger",
                     "suffire",
                     "atteindre",
                     "annoncer",
                     "élever",
                     "acheter",
                     "mener",
                     "préparer",
                     "assurer",
                     "deviner",
                     "considérer",
                     "appartenir",
                     "représenter",
                     "tromper",
                     "vendre",
                     "craindre",
                     "emporter",
                     "rouler",
                     "posséder",
                     "réveiller",
                     "aider",
                     "découvrir",
                     "choisir",
                     "prononcer",
                     "taire",
                     "rêver",
                     "appuyer",
                     "étendre",
                     "trembler",
                     "défendre",
                     "créer",
                     "maintenir",
                     "indiquer",
                     "promettre",
                     "relever",
                     "abandonner",
                     "ignorer",
                     "exprimer",
                     "accompagner",
                     "adresser",
                     "observer",
                     "séparer",
                     "marier",
                     "prévoir",
                     "amener",
                     "obliger",
                     "éclairer",
                     "poursuivre",
                     "livrer",
                     "contenir",
                     "fuir",
                     "couler",
                     "proposer",
                     "éprouver",
                     "retenir",
                     "attacher",
                     "voler",
                     "surprendre",
                     "briser",
                     "imaginer",
                     "diriger",
                     "parvenir",
                     "pénétrer",
                     "remarquer",
                     "éviter",
                     "établir",
                     "réussir",
                     "pencher",
                     "habiter",
                     "entourer",
                     "déclarer",
                     "étonner",
                     "dresser",
                     "durer",
                     "fixer",
                     "désirer",
                     "arracher",
                     "entraîner",
                     "soutenir",
                     "couper",
                     "douter",
                     "retirer",
                     "promener",
                     "forcer",
                     "examiner",
                     "revoir",
                     "remplir",
                     "terminer",
                     "tenter",
                     "remonter",
                     "installer",
                     "soulever",
                     "allumer",
                     "imposer",
                     "respirer",
                     "baisser",
                     "souffler",
                     "attirer",
                     "prêter",
                     "amuser",
                     "éclater",
                     "réunir",
                     "traiter",
                     "traîner",
                     "employer",
                     "marquer",
                     "prouver",
                     "importer",
                     "exiger",
                     "reposer",
                     "danser",
                     "saluer",
                     "accorder",
                     "achever",
                     "avouer",
                     "distinguer",
                     "emmener",
                     "agiter",
                     "hésiter",
                     "sonner",
                     "composer",
                     "enlever",
                     "rejoindre",
                     "ramener",
                     "étudier",
                     "partager",
                     "chasser",
                     "interrompre",
                     "éloigner",
                     "réduire",
                     "engager",
                     "éteindre",
                     "recommencer",
                     "sauter",
                     "plaindre",
                     "préférer",
                     "révéler",
                     "subir",
                     "rapporter",
                     "coûter",
                     "réfléchir",
                     "remercier",
                     "déposer",
                     "fumer",
                     "affirmer",
                     "convenir",
                     "vêtir",
                     "accomplir",
                     "résoudre",
                     "plonger",
                     "détruire",
                     "intéresser",
                     "disposer",
                     "lisser",
                     "verser",
                     "obéir",
                     "lutter",
                     "prétendre",
                     "construire",
                     "soumettre",
                     "peser",
                     "troubler",
                     "répandre",
                     "résister",
                     "protéger",
                     "enfermer",
                     "creuser",
                     "grandir",
                     "enfoncer",
                     "envelopper",
                     "prévenir",
                     "inspirer",
                     "ramasser",
                     "endormir",
                     "inventer",
                     "presser",
                     "confier",
                     "effacer",
                     "reculer",
                     "user",
                     "nourrir",
                     "remplacer",
                     "souhaiter",
                     "signer",
                     "interroger",
                     "dominer",
                     "commander",
                     "supposer",
                     "dépasser",
                     "accuser",
                     "habiller",
                     "condamner",
                     "menacer",
                     "écraser",
                     "céder",
                     "écarter",
                     "réclamer",
                     "dessiner",
                     "conclure",
                     "lier",
                     "admettre",
                     "attaquer",
                     "respecter",
                     "pendre",
                     "supporter",
                     "figurer",
                     "profiter",
                     "accrocher",
                     "calmer",
                     "satisfaire",
                     "valoir",
                     "signifier",
                     "inquiéter",
                     "assister",
                     "inviter",
                     "déchirer",
                     "risquer",
                     "parcourir",
                     "rejeter",
                     "renoncer",
                     "veiller",
                     "transformer",
                     "tracer",
                     "contenter",
                     "mériter",
                     "précipiter",
                     "rompre",
                     "caresser",
                     "étouffer",
                     "animer",
                     "casser",
                     "fonder",
                     "franchir",
                     "abattre",
                     "discuter",
                     "fatiguer",
                     "consentir",
                     "regretter",
                     "joindre",
                     "vaincre",
                     "consulter",
                     "haïr",
                     "repousser",
                     "exécuter",
                     "exposer",
                     "voyager",
                     "renverser",
                     "rassurer",
                     "retomber",
                     "décrire",
                     "mentir",
                     "armer",
                     "étaler",
                     "essuyer",
                     "précéder",
                     "désigner",
                     "détacher",
                     "recueillir",
                     "croiser",
                     "entretenir",
                     "surveiller",
                     "réserver",
                     "confondre",
                     "dégager",
                     "parer",
                     "visiter",
                     "détourner",
                     "plier",
                     "accueillir",
                     "redevenir",
                     "approuver",
                     "emparer",
                     "aborder",
                     "heurter",
                     "noyer",
                     "semer",
                     "guider",
                     "piquer",
                     ]
