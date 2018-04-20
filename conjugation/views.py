from django.http import JsonResponse
from django.shortcuts import render, redirect, Http404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from unidecode import unidecode

from conjugation.models import Verb as V
from .utils import FORMULAS, TEMPLATE_NAME, FORMULAS_PASSIVE


@csrf_exempt
def search(request):
    search_string = request.POST.get('verb')
    # verb(request, se=False, feminin=False, verb=search_string)
    return redirect(reverse('conjugation:verb', kwargs={'verb': search_string}))


def index(request):
    return render(request, 'conjugation/index.html')


def verb(request, se, feminin, verb):

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

    if se or v.reflexive_only:
        reflexive = True
    else:
        reflexive = False

    if v.reflexive:
        pass

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
            dict(url=reverse('conjugation:verb', args=[verb.infinitive_no_accents]), verb=verb.infinitive, html=html))
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
        self.persons = self.get_persons_list(gender, reflexive)

    def get_persons_list(self, gender, reflexive):
        persons = []
        tense_dict = FORMULAS[self.mood_name][self.tense_name]
        for person_name in tense_dict[1].keys():
            person = Person(self.v, self.mood_name, self.tense_name, person_name, gender, reflexive)
            persons.append(person)
        return persons

    def is_in_short_list(self):
        pass

    def __str__(self):
        return self.tense_name


class Person:
    VOWELS = ['a', 'e', 'i', 'o', 'u', 'y', 'â', 'ê', 'è', 'é', 'ô', 'œ', 'î', 'ê', 'î', 'ï', 'à', 'ä', 'ë', 'ö', 'û', 'ì']

    def __init__(self, v: V, mood_name: str, tense_name: str, person_name: str, gender: int, reflexive: bool):
        self.v = v
        self.mood_name = mood_name
        self.tense_name = tense_name
        self.person_name = person_name

        pronoun = -1 if v.infnitive_first_letter_is_vowel() else 0
        maison = 1 if self.v.maison else 2
        self.part_0, self.forms, self.part_2 = self.get_parts(maison, 0, gender, pronoun, reflexive)
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
            parts = FORMULAS_PASSIVE[self.mood_name][self.tense_name][maison][self.person_name][switch]
        path_to_conjugation = parts[1][gender]
        if path_to_conjugation == None:
            return '-', '', ''
        verb_forms = self.v.conjugations[path_to_conjugation[0]][path_to_conjugation[1]][int(path_to_conjugation[2])]
        return parts[0][gender][pronoun], verb_forms, parts[2][gender][pronoun]

    def __str__(self):
        return self.person_name
