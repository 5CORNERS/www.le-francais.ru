from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from unidecode import unidecode

from conjugation.models import Verb as V, ReflexiveVerb as RV
from .utils import FORMULAS, TEMPLATE_NAME, FORMULAS_PASSIVE, SHORT_LIST, FORMULAS_PASSIVE_X


@csrf_exempt
def search(request):
    try:
        search_string = unidecode(request.POST.get('verb'))
    except:
        return redirect(reverse('conjugation:index'))
    if search_string[:2] == "s'" or search_string[:3] == "se ":
        try:
            re_verb=RV.objects.get(infinitive_no_accents=search_string)
        except:
            return render(request,'conjugation/verb_not_found.html', {'search_string':search_string})
        return redirect(re_verb.url())
    try:
        verb = V.objects.get(infinitive_no_accents=search_string)
    except:
        return render(request,'conjugation/verb_not_found.html', {'search_string':search_string})
    return redirect(verb.url())


def index(request):
    FREQUENT_URLS = [
        '''<a href="/conjugaison/etre">être</a>''',
        '''<a href="/conjugaison/avoir">avoir</a>''',
        '''<a href="/conjugaison/faire">faire</a>''',
        '''<a href="/conjugaison/dire">dire</a>''',
        '''<a href="/conjugaison/pouvoir">pouvoir</a>''',
        '''<a href="/conjugaison/aller">aller</a>''',
        '''<a href="/conjugaison/voir">voir</a>''',
        '''<a href="/conjugaison/vouloir">vouloir</a>''',
        '''<a href="/conjugaison/venir">venir</a>''',
        '''<a href="/conjugaison/devoir">devoir</a>''',
        '''<a href="/conjugaison/prendre">prendre</a>''',
        '''<a href="/conjugaison/trouver">trouver</a>''',
        '''<a href="/conjugaison/donner">donner</a>''',
        '''<a href="/conjugaison/falloir">falloir</a>''',
        '''<a href="/conjugaison/parler">parler</a>''',
        '''<a href="/conjugaison/mettre">mettre</a>''',
        '''<a href="/conjugaison/savoir">savoir</a>''',
        '''<a href="/conjugaison/passer">passer</a>''',
        '''<a href="/conjugaison/regarder">regarder</a>''',
        '''<a href="/conjugaison/aimer">aimer</a>''',
        '''<a href="/conjugaison/croire">croire</a>''',
        '''<a href="/conjugaison/demander">demander</a>''',
        '''<a href="/conjugaison/rester">rester</a>''',
        '''<a href="/conjugaison/repondre">répondre</a>''',
        '''<a href="/conjugaison/entendre">entendre</a>''',
        '''<a href="/conjugaison/penser">penser</a>''',
        '''<a href="/conjugaison/arriver">arriver</a>''',
        '''<a href="/conjugaison/connaitre">connaître</a>''',
        '''<a href="/conjugaison/devenir">devenir</a>''',
        '''<a href="/conjugaison/sentir">sentir</a>''',
        '''<a href="/conjugaison/sembler">sembler</a>''',
        '''<a href="/conjugaison/tenir">tenir</a>''',
        '''<a href="/conjugaison/comprendre">comprendre</a>''',
        '''<a href="/conjugaison/rendre">rendre</a>''',
        '''<a href="/conjugaison/attendre">attendre</a>''',
        '''<a href="/conjugaison/sortir">sortir</a>''',
        '''<a href="/conjugaison/vivre">vivre</a>''',
        '''<a href="/conjugaison/reprendre">reprendre</a>''',
        '''<a href="/conjugaison/entrer">entrer</a>''',
        '''<a href="/conjugaison/porter">porter</a>''',
        '''<a href="/conjugaison/chercher">chercher</a>''',
        '''<a href="/conjugaison/revenir">revenir</a>''',
        '''<a href="/conjugaison/appeler">appeler</a>''',
    ]
    return render(request, 'conjugation/index.html', dict(frequent_urls=FREQUENT_URLS))


def verb(request, se, feminin, verb, homonym):

    verb_no_accent = unidecode(verb)
    try:
        v = V.objects.get(infinitive_no_accents=verb_no_accent)
    except V.DoesNotExist:
        return render(request,'conjugation/verb_not_found.html', {'search_string':verb_no_accent})



    if feminin:
        feminin = True
        gender = -1
    else:
        feminin = False
        gender = 0

    if v.reflexive_only and not se:
        return redirect(v.reflexiveverb.url())
    if not (v.reflexive_only or v.can_reflexive) and se:
        return redirect(v.url())


    reflexive = v.can_reflexive and se

    v.count += 1
    v.save()
    v.construct_conjugations()
    table = Table(v, gender, reflexive)
    template_name = 'conjugation/table.html'
    return render(request, template_name, {'v':v, 'reflexive':reflexive,'feminin':feminin, 'table': table, 'forms_count': v.template.forms_count, 'forms_range': list(range(1, v.template.forms_count + 1))})


def switch_keyboard_layout(s: str):
    LAYOUT_EN = '''`~!@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?'''
    LAYOUT_RU = '''ёЁ!"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'''
    for n in range(LAYOUT_EN.__len__()):
        s = s.replace(LAYOUT_RU[n], LAYOUT_EN[n])
    return s


def get_autocomplete_list(request):
    list_len = 50
    _term = request.GET['term'].lower()
    term = unidecode(_term)

    if term[:3] == 'se ' or term[:2] == "s'":
        C = RV
    else:
        C = V
    q_startswith = C.objects.filter(infinitive_no_accents__startswith=term)

    if q_startswith.__len__() == 0:
        term = switch_keyboard_layout(_term)
        q_startswith = C.objects.filter(infinitive_no_accents__startswith=term)

    if q_startswith.__len__() < list_len:
        q_contains = C.objects.filter(infinitive_no_accents__contains=term).difference(q_startswith)
        q = list(q_startswith) + list(q_contains)
    else:
        q = q_startswith

    autocomplete_list = []
    term_len = term.__len__()
    for v in q[0:list_len]:
        if not isinstance(v, RV) and v.reflexive_only:
            v = v.reflexiveverb
        pos_start = v.infinitive_no_accents.find(term)
        pos_end = pos_start + term_len
        html = v.infinitive[0:pos_start] + '<b>' + v.infinitive[pos_start:pos_end] + '</b>' + v.infinitive[pos_end:]


        autocomplete_list.append(
            dict(url=v.url(), verb=v.infinitive, html=html))
    return JsonResponse(autocomplete_list, safe=False)


class Table:
    def __init__(self, v: V, gender: int, reflexive: bool):
        self.v = v
        self.t = v.template
        self.moods = self.get_moods_list(gender, reflexive)

    def get_moods_list(self, gender, reflexive):
        moods = []
        for mood_name in FORMULAS.keys():
            mood = Mood(self.v, mood_name, gender, reflexive)
            moods.append(mood)
        return moods

    def __str__(self):
        return self.v.infinitive + ' Table Object'


class Mood:
    def __init__(self, v, mood_name, gender: int, reflexive: bool):
        self.name = TEMPLATE_NAME[mood_name]
        self.v = v
        self.mood_name = mood_name
        self.tenses = self.get_tenses_list(gender, reflexive)

    def get_tenses_list(self, gender, reflexive):
        tenses = []
        mood_dict = FORMULAS[self.mood_name]
        for tense_name in mood_dict.keys():
            tense = Tense(self.v, self.mood_name, tense_name, gender, reflexive)
            tenses.append(tense)
        return tenses

    def __str__(self):
        return self.mood_name


class Tense:
    def __init__(self, v: V, moode_name, tense_name, gender: int, reflexive: bool):
        self.name = TEMPLATE_NAME[tense_name]
        self.v = v
        self.tense_name = tense_name
        self.mood_name = moode_name
        self.gender = gender
        self.reflexive = reflexive
        self.persons = self.get_persons_list()

    def get_persons_list(self):

        if self.reflexive:
            rv = self.v.reflexiveverb
            if rv.is_deffective:
                deffective_patterns = rv.deffective
                if deffective_patterns.has_mood_tense(self.mood_name, self.tense_name):
                    return self.get_empty_persons_list()
        else:
            if self.v.is_deffective:
                deffective_patterns = self.v.deffective
                if deffective_patterns.has_mood_tense(self.mood_name, self.tense_name):
                    return self.get_empty_persons_list()

        persons = []
        tense_dict = FORMULAS[self.mood_name][self.tense_name]
        for person_name in tense_dict[1].keys():
            person = Person(self.v, self.mood_name, self.tense_name, person_name, self.gender, self.reflexive)
            persons.append(person)
        return persons

    def is_in_short_list(self):
        return True if self.tense_name in SHORT_LIST[self.mood_name] else False

    def __str__(self):
        return self.tense_name

    def get_empty_persons_list(self):
        persons = []
        tense_dict = FORMULAS[self.mood_name][self.tense_name]
        for person_name in tense_dict[1].keys():
            person = Person(self.v, self.mood_name, self.tense_name, person_name, self.gender, self.reflexive, empty=True)
            persons.append(person)
        return persons


class Person:
    VOWELS_LIST = ['a', 'ê', 'é', 'h', 'e', 'â', 'i', 'o', 'ô', 'u', 'w', 'y', 'œ', ]

    def __init__(self, v: V, mood_name: str, tense_name: str, person_name: str, gender: int, reflexive: bool, empty=False):
        self.v = v
        self.mood_name = mood_name
        self.tense_name = tense_name
        self.person_name = person_name

        pronoun = -1 if v.infnitive_first_letter_is_vowel() else 0
        etre = 2 if not self.v.conjugated_with_avoir and self.v.conjugated_with_etre else 1
        if empty:
            self.part_0, self.forms, self.part_2 = '-','',''
        else:
            self.part_0, self.forms, self.part_2 = self.get_parts(etre, 0, gender, pronoun, reflexive)
        if not isinstance(self.forms, list):
            self.forms = [self.forms]

    def more_than_one(self):
        if len(self.forms) > 1:
            return True
        else:
            return False

    def get_parts(self, maison, switch, gender, pronoun, reflexive):
        if not reflexive:
            parts = FORMULAS[self.mood_name][self.tense_name][maison][self.person_name][switch]
        else:
            if self.v.infinitive in [
            "plaire",
            "complaire",
            "déplaire",
            "rire",
            "convenir",
            "nuire",
            "mentir",
            "ressembler",
            "sourire",
            "suffire",
            "survivre",
            "acheter",
            "succéder",
            "téléphoner",
            "parler",
            "demander",
            "ntre-nuire",
            ]:
                parts = FORMULAS_PASSIVE_X[self.mood_name][self.tense_name][maison][self.person_name][switch]
            else:
                parts = FORMULAS_PASSIVE[self.mood_name][self.tense_name][maison][self.person_name][switch]
        path_to_conjugation = parts[1][gender]
        if path_to_conjugation == None:
            return '-', '', ''
        verb_forms = self.v.conjugations[path_to_conjugation[0]][path_to_conjugation[1]][int(path_to_conjugation[2])]
        if verb_forms == None:
            return '-', '', ''

        if isinstance(verb_forms, list):
            pronoun = -1 if verb_forms[0][0] in self.VOWELS_LIST else 0
        else:
            pronoun = -1 if verb_forms[0] in self.VOWELS_LIST else 0

        return parts[0][gender][pronoun], verb_forms, parts[2][gender][pronoun]

    def __str__(self):
        return self.person_name
