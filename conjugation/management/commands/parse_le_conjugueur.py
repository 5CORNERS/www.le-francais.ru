import json
import re
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup, Tag
from django.core.management import BaseCommand
from requests.utils import default_headers

from conjugation.consts import VOWELS_LIST
from conjugation.models import Verb
from conjugation.utils import search_verbs_with_forms

MOODS_TO_KEYS = {
	'Indicatif': 'indicative',
	'Subjonctif': 'subjunctive',
	'Conditionnel': 'conditional',
	'Impératif': 'imperative',
	'Participe': 'participle',
	'Infinitif': 'infinitive',
	'Gérondif': 'gerund',
}

# TODO: totally rework this
TENSES_TO_KEYS = {
	'Présent': 'present',
	'Passé simple': 'simple-past',
	'Passé composé': 'composé-past',
	'Passé antérieur': 'antérieur-past',
	'Imparfait': 'imperfect',
	'Futur simple': 'future',
	'Plus-que-parfait': 'pluperfect',
	'Futur antérieur': 'antérieur-future',
	'Passé': 'past',
	'Passé première forme': 'past-first',
	'Passé deuxième forme': 'past-second',
}

TEMPLATE_VERBS = {
	'VERB_INFINITIVE': ["infinitive", "infinitive-present", "0"],
	'VERB_PRESENT_1': ["indicative", "present", "0"],
	'VERB_PRESENT_2': ["indicative", "present", "1"],
	'VERB_PRESENT_3': ["indicative", "present", "2"],
	'VERB_PRESENT_4': ["indicative", "present", "3"],
	'VERB_PRESENT_5': ["indicative", "present", "4"],
	'VERB_PRESENT_6': ["indicative", "present", "5"],
	'VERB_IMPERFECT_1': ["indicative", "imperfect", "0"],
	'VERB_IMPERFECT_2': ["indicative", "imperfect", "1"],
	'VERB_IMPERFECT_3': ["indicative", "imperfect", "2"],
	'VERB_IMPERFECT_4': ["indicative", "imperfect", "3"],
	'VERB_IMPERFECT_5': ["indicative", "imperfect", "4"],
	'VERB_IMPERFECT_6': ["indicative", "imperfect", "5"],
	'VERB_FUTURE_1': ["indicative", "future", "0"],
	'VERB_FUTURE_2': ["indicative", "future", "1"],
	'VERB_FUTURE_3': ["indicative", "future", "2"],
	'VERB_FUTURE_4': ["indicative", "future", "3"],
	'VERB_FUTURE_5': ["indicative", "future", "4"],
	'VERB_FUTURE_6': ["indicative", "future", "5"],
	'VERB_SIMPLE_PAST_1': ["indicative", "simple-past", "0"],
	'VERB_SIMPLE_PAST_2': ["indicative", "simple-past", "1"],
	'VERB_SIMPLE_PAST_3': ["indicative", "simple-past", "2"],
	'VERB_SIMPLE_PAST_4': ["indicative", "simple-past", "3"],
	'VERB_SIMPLE_PAST_5': ["indicative", "simple-past", "4"],
	'VERB_SIMPLE_PAST_6': ["indicative", "simple-past", "5"],
	'VERB_SUBJUNCTIVE_PRESENT_1': ["subjunctive", "present", "0"],
	'VERB_SUBJUNCTIVE_PRESENT_2': ["subjunctive", "present", "1"],
	'VERB_SUBJUNCTIVE_PRESENT_3': ["subjunctive", "present", "2"],
	'VERB_SUBJUNCTIVE_PRESENT_4': ["subjunctive", "present", "3"],
	'VERB_SUBJUNCTIVE_PRESENT_5': ["subjunctive", "present", "4"],
	'VERB_SUBJUNCTIVE_PRESENT_6': ["subjunctive", "present", "5"],
	'VERB_SUBJUNCTIVE_IMPERFECT_1': ["subjunctive", "imperfect", "0"],
	'VERB_SUBJUNCTIVE_IMPERFECT_2': ["subjunctive", "imperfect", "1"],
	'VERB_SUBJUNCTIVE_IMPERFECT_3': ["subjunctive", "imperfect", "2"],
	'VERB_SUBJUNCTIVE_IMPERFECT_4': ["subjunctive", "imperfect", "3"],
	'VERB_SUBJUNCTIVE_IMPERFECT_5': ["subjunctive", "imperfect", "4"],
	'VERB_SUBJUNCTIVE_IMPERFECT_6': ["subjunctive", "imperfect", "5"],
	'VERB_CONDITIONAL_PRESENT_1': ["conditional", "present", "0"],
	'VERB_CONDITIONAL_PRESENT_2': ["conditional", "present", "1"],
	'VERB_CONDITIONAL_PRESENT_3': ["conditional", "present", "2"],
	'VERB_CONDITIONAL_PRESENT_4': ["conditional", "present", "3"],
	'VERB_CONDITIONAL_PRESENT_5': ["conditional", "present", "4"],
	'VERB_CONDITIONAL_PRESENT_6': ["conditional", "present", "5"],
	'VERB_IMPERATIVE_PRESENT_II_S': ["imperative", "imperative-present", "0"],
	'VERB_IMPERATIVE_PRESENT_I_P': ["imperative", "imperative-present", "1"],
	'VERB_IMPERATIVE_PRESENT_II_P': ["imperative", "imperative-present", "2"],
	'VERB_PRESENT_PARTICIPLE': ["participle", "present-participle", "0"],
	'VERB_PAST_PARTICIPLE_S_M': ["participle", "past-participle", "0"],
	'VERB_PAST_PARTICIPLE_S_F': ["participle", "past-participle", "2"],
	'VERB_PAST_PARTICIPLE_P_M': ["participle", "past-participle", "1"],
	'VERB_PAST_PARTICIPLE_P_F': ["participle", "past-participle", "3"]
}
COMPLICATED_TENSES = {
	('indicative', 'past'): 'past-participle',
	('indicative', 'composé-past'):'past-participle',
	('indicative', 'antérieur-past'):'past-participle',
	('indicative', 'antérieur-future'):'past-participle',
	('indicative', 'pluperfect'):'past-participle',
	('subjunctive', 'past'): 'past-participle',
	('subjunctive', 'pluperfect'): 'past-participle',
	('conditional', 'past-first'): 'past-participle',
	('conditional', 'past-second'): 'past-participle',
	('imperative', 'past'): 'past-participle',
	('imperative', 'present'): 'imperative-present',
	('infinitive', 'past'): 'past-participle',
	('infinitive', 'present'): 'infinitive-present',
	('gerund', 'past'): 'past-participle',
	('gerund', 'present'): 'present-participle',
	('participle', 'present'): 'present-participle',
	('participle', 'past'): 'past-participle',




}
FORMULAS_SWITCHES = {
	'':"",
	'question': "QUESTION",
    'question-pronominal-en': 'QUESTION_S-EN',
	'question-pronominal': "QUESTION_REFLEXIVE",
    'question-pronominal-en-negation': 'QUESTION_S-EN_NEGATIVE',
	'question-pronominal-negation': "QUESTION_REFLEXIVE_NEGATIVE",
	'question-negation': "QUESTION_NEGATIVE",
	'question-negation-voix-passive': "QUESTION_NEGATIVE_PASSIVE",
	'question-voix-passive': "QUESTION_PASSIVE",
    'pronominal-en': "S-EN",
	'pronominal': "REFLEXIVE",
    'pronominal-en-negation': 'S-EN_NEGATIVE',
	'pronominal-negation': "REFLEXIVE_NEGATIVE",
	'negation': "NEGATIVE",
	'negation-voix-passive': "NEGATIVE_PASSIVE",
	'voix-passive': "PASSIVE",
}
PERSONS_SIMPLE = [
	'person_I_S',
	'person_II_S',
	'person_III_S',
	'person_I_P',
	'person_II_P',
	'person_III_P',
]

PERSONS_IMPERATIVE = [
	'person_II_S',
	'person_I_P',
	'person_II_P',
]
PERSONS_PARTICIPLE_PRESENT = [
	'singular',
]
PERSONS_PARTICIPLE_PAST = [
	'singular',
	'singular',
	'plural',
	'plural',
	'compose',
]
PERSONS_INFINITIVE = [
	'person_I_S'
]

ETRE = 'etre'
AVOIR = 'avoir'

MASCULINE = 'm'
FEMININE = 'f'

VOWEL = 'vowel_1'
NOT_VOWEL = 'vowel_0'

def get_persons_list(mood, tense):
	if mood == 'imperative':
		return PERSONS_IMPERATIVE
	elif mood == 'participle':
		if tense == 'present':
			return PERSONS_PARTICIPLE_PRESENT
		elif tense == 'past':
			return PERSONS_PARTICIPLE_PAST
	elif mood in ['infinitive', 'gerunf']:
		return PERSONS_INFINITIVE
	return PERSONS_SIMPLE

SLEEP_DURATION_BETWEEN_REQUESTS = 30


class Command(BaseCommand):
	def handle(self, *args, **options):
		formulas = {}
		for path in Path(
				'conjugation/data/parse_conjugations/input').iterdir():
			with path.open('r', encoding='utf-8') as f:
				for line in f:
					url: str
					h, infinitive, switch, url = line.rstrip('\n').split('\t')
					verb = Verb.objects.get(infinitive=infinitive)
					conjugations = parse_le_conjugueur_url(url=url, verb=verb)
					if '_' in url:
						url_fem = url.replace('.html', '-feminin.html')
					else:
						url_fem = url.replace('.html', '_feminin.html')
					conjugations_fem = parse_le_conjugueur_url(url=url_fem, verb=verb)
					switch = FORMULAS_SWITCHES[switch]
					formulas = update_switch(conjugations, formulas, switch, verb)
					formulas = update_switch(conjugations_fem, formulas, switch, verb, gender=FEMININE)
		formulas = merge_empty_values(formulas)
		with open('conjugation/data/parse_conjugations/output/output.json','w', encoding='utf-8') as out:
			json.dump(formulas, out)

def merge_empty_values(node:dict):
	for key, value in node.items():
		if isinstance(value, dict):
			node[key] = merge_empty_values(value)
			if key in ['part_1', 'part_2']:
				if value[MASCULINE] == {VOWEL: None, NOT_VOWEL: None}:
					node[key][MASCULINE] = value[FEMININE]
				elif value[FEMININE] == {VOWEL: None, NOT_VOWEL: None}:
					node[key][FEMININE] = value[MASCULINE]
			elif key in [MASCULINE, FEMININE] and VOWEL in value.keys():
				if value[VOWEL] is None:
					node[key][VOWEL] = value[NOT_VOWEL]
				elif value[NOT_VOWEL] is None:
					node[key][NOT_VOWEL] = value[VOWEL]
			elif key == 'verb_part':
				if value[MASCULINE] is None:
					node[key][MASCULINE] = value[FEMININE]
				elif value[FEMININE] is None:
					node[key][FEMININE] = value[MASCULINE]
	return node



def merge(source:dict, destination:dict):
	for key, value in source.items():
		if isinstance(value, dict):
			node = destination.setdefault(key, {})
			merge(value, node)
		elif value is not None:
			destination[key] = value
		else:
			continue
	return destination


def update_switch(conjugations:dict, formulas:dict, switch:str, verb:Verb, gender=MASCULINE):
	if not switch in formulas.keys():
		formulas[switch] = {}
	etre_or_avoir = AVOIR if not verb.conjugated_with_etre else ETRE
	for mood, tenses in conjugations.items():
		if not mood in formulas[switch].keys():
			formulas[switch][mood] = {}
		for tense, persons in tenses.items():
			if not tense in formulas[switch][mood].keys():
				formulas[switch][mood][tense] = {ETRE:{}, AVOIR:{}}
			person_list = get_persons_list(mood, tense)
			# le figaro participle passe
			if mood == 'participle' and tense == 'past':
				genders = [
					MASCULINE,
					FEMININE,
					MASCULINE,
					FEMININE,
					MASCULINE
				]
				for i, line in enumerate(persons):
					person_key = person_list[i]
					g = genders[i]
					line_result = parse_line(line, verb, tense, mood, str(i), g, switch)
					formulas = merge_line_result(etre_or_avoir, formulas, line_result, mood, person_key, switch, tense)
			else:
				for i, line in enumerate(persons):
					person_key = person_list[i]
					line_result = parse_line(line, verb, tense, mood, str(i), gender, switch)
					formulas = merge_line_result(etre_or_avoir, formulas, line_result, mood, person_key, switch, tense)
	return formulas


def merge_line_result(etre, formulas, line_result, mood, person_key, switch, tense):
	if not person_key in formulas[switch][mood][tense][etre]:
		formulas[switch][mood][tense][etre][person_key] = line_result
	else:
		old_result = formulas[switch][mood][tense][etre][person_key]
		formulas[switch][mood][tense][etre][person_key] = merge(line_result, old_result)
	return formulas


def parse_le_conjugueur_url(url, verb, check_identity=False):
	temp = Path(f'conjugation/data/parse_conjugations/temp/html/{url.split("/")[-1]}')
	temp_wo_html = Path(f'conjugation/data/parse_conjugations/temp/html/{url.split("/")[-1].replace(".html","")}')
	print(f'Parsing {url}')
	if temp.exists():
		body = temp.read_bytes()
	elif temp_wo_html.exists():
		body = temp_wo_html.read_bytes()
	else:
		headers = default_headers()
		headers.update({
			'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
		})
		req = requests.get(url, headers)
		body = req.content
		temp.touch()
		temp.write_bytes(body)
		sleep(SLEEP_DURATION_BETWEEN_REQUESTS)
	return parse_le_conjugueur_html(html=body, check_identity=check_identity, url=url)


def parse_le_conjugueur_html(html, check_identity=False, url=None):
	soup = BeautifulSoup(html, features="html5lib")
	mood_tag: Tag
	results = {}
	identity = True
	if check_identity and url is not None:
		title_tag = soup.find("div", class_="verbe").find("h1")
		if 'pronominal-en' in url and not 's\'en' in title_tag.text:
			identity = False
		elif 'pronominal' in url and 's\'en' in title_tag.text:
			identity = False
	for mood_tag in soup.find_all("div", class_="modeBloc"):
		# le_conjugueur uses the modeBloc class w/o conjugations
        # skipping tags w/o conjugations
		if not mood_tag.text in MOODS_TO_KEYS.keys():
			continue
		mood = MOODS_TO_KEYS[mood_tag.text]
		mood_key = mood
		results[mood_key] = {}
		tense_tag = mood_tag.next_sibling
		end_of_mood = False
		while not end_of_mood:
			# skipping empty tense tags
			if tense_tag.find(class_='tempsBloc') is not None:
				tense = tense_tag.find(class_='tempsBloc').text
				tense_key = TENSES_TO_KEYS[tense]
				results[mood_key][tense_key] = []
				# replacing <br> tags with newlines
				for br_tag in tense_tag.find_all('br'):
					br_tag.replace_with("\n" + br_tag.text)
				# getting last <p> with conjugations
                # splitting tense lines by \n
				lines = tense_tag.find_all("p")[-1].text.split("\n")
				for line in lines:
					results[mood_key][tense_key].append(line)
			tense_tag = tense_tag.next_sibling
			# checking is there next tense
			if 'class' not in tense_tag.attrs.keys() or not 'conjugBloc' in tense_tag.attrs[
				'class']:
				end_of_mood = True
	if check_identity:
		return results, identity
	else:
		return results


def parse_line(line, verb, line_tense, line_mood, line_person, gender=MASCULINE, switch=None):
	result = {
		'part_1': {
			MASCULINE: {
				VOWEL: None,
				NOT_VOWEL: None,
			},
			FEMININE: {
				VOWEL: None,
				NOT_VOWEL: None,
			},
		},
		'verb_part': {
			MASCULINE:None,
			FEMININE:None,
		},
		'part_2': {
			MASCULINE: {
				VOWEL: None,
				NOT_VOWEL: None,
			},
			FEMININE: {
				VOWEL: None,
				NOT_VOWEL: None,
			},
		},
	}
	part_1 = None
	part_2 = None
	verb_key = None
	verb_form = None
	matches = []
	for word in re.findall(r"[\w]+", line):
		matches.append(re.match(f'^.*({word}).*$', line))
	for match in matches:
		for found_verb, forms in search_verbs_with_forms(match.group(1), exact=True):
			if found_verb != verb:
				continue
			for form, form_mood, form_tense, form_person, n in forms:
				for key, value in TEMPLATE_VERBS.items():
					if form_mood in value and form_tense in value and str(form_person) in value:
						if (
								form_mood == line_mood and form_tense == line_tense and
								str(form_person) == line_person
						) or (
								((line_mood, line_tense) in COMPLICATED_TENSES.keys() and
								 form_tense == COMPLICATED_TENSES[line_mood, line_tense])
						) or (
                            'PASSIVE' in switch and form_tense == 'past-participle'
                        ):
							part_1 = line[:match.start(1)]
							part_2 = line[match.end(1):]
							verb_form = form
							verb_key = key
	if verb_form is not None:
		starts_with_vowel = VOWEL if verb_form[0] in VOWELS_LIST else NOT_VOWEL
		ends_with_vowel = VOWEL if verb_form[-1] in VOWELS_LIST else NOT_VOWEL
		if part_1 is not None:
			result['part_1'][gender][starts_with_vowel] = part_1
		if part_2 is not None:
			result['part_2'][gender][ends_with_vowel] = part_2
		if verb_key is not None:
			result['verb_part'][gender] = verb_key
	return result
