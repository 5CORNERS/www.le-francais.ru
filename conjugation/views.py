from re import sub

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from unidecode import unidecode

from conjugation.models import Verb, ReflexiveVerb, PollyAudio
from polly.models import PollyTask
from .consts import *
from .polly import *
from .utils import FORMULAS, TEMPLATE_NAME, FORMULAS_PASSIVE, SHORT_LIST, FORMULAS_PASSIVE_X


@require_http_methods(["POST"])
def get_polly_audio_link(request):
	key = request.POST.get('key')
	polly_audio, created = PollyAudio.objects.select_related('polly').get_or_create(key=key)
	if created or polly_audio.polly is None or polly_audio.polly.url is None:
		tense = Tense(key=key)
		polly_task = PollyTask(
			text=tense.get_polly_ssml(),
			text_type=TEXT_TYPE_SSML,
			language_code=LANGUAGE_CODE_FR,
			sample_rate=SAMPLE_RATE_22050,
			voice_id=VOICE_ID_LEA,
			output_format=OUTPUT_FORMAT_MP3,
		)
		polly_task.create_task('polly-conjugations/', wait=True, save=True)
		polly_audio.polly = polly_task
		polly_audio.save()
	return JsonResponse(data={key: {'url': polly_audio.polly.url}})


@csrf_exempt
def search(request):
	search_string = unidecode(switch_keyboard_layout(str(request.POST.get('verb')).strip(' ').lower()))

	if search_string[:2] == "s'" or search_string[:3] == "se ":
		try:
			re_verb = ReflexiveVerb.objects.get(infinitive_no_accents=search_string)
		except ReflexiveVerb.DoesNotExist:
			return render(request, 'conjugation/verb_not_found.html',
			              {'search_string': search_string})
		except ReflexiveVerb.MultipleObjectsReturned:
			re_verb = ReflexiveVerb.objects.filter(infinitive_no_accents=search_string).first()
		return redirect(re_verb.get_absolute_url())

	try:
		verb = Verb.objects.get(infinitive_no_accents=search_string)
	except Verb.DoesNotExist:
		return render(request, 'conjugation/verb_not_found.html',
		              {'search_string': search_string})
	except Verb.MultipleObjectsReturned:
		verb = Verb.objects.filter(infinitive_no_accents=search_string).first()
	return redirect(verb.get_absolute_url())


def index(request):
	return render(request, 'conjugation/index.html', dict(frequent_urls=FREQUENT_URLS))


def verb_page(request, se, feminin, verb, homonym):
	word_no_accent = unidecode(verb)
	try:
		verb = Verb.objects.get(infinitive_no_accents=word_no_accent)
	except Verb.DoesNotExist:
		return render(request, 'conjugation/verb_not_found.html',
		              {'search_string': word_no_accent})
	except Verb.MultipleObjectsReturned:
		verb = Verb.objects.get(infinitive=word_no_accent)

	if feminin:
		feminin = True
		gender = -1
	else:
		feminin = False
		gender = 0

	if verb.reflexive_only and not se:
		return redirect(verb.reflexiveverb.get_absolute_url())
	if not (verb.reflexive_only or verb.can_reflexive) and se:
		return redirect(verb.get_absolute_url())

	if (se == "se_" and verb.reflexiveverb.is_short()) or (se == "s_" and not verb.reflexiveverb.is_short()):
		return redirect(verb.reflexiveverb.get_absolute_url())

	reflexive = True if (verb.can_reflexive or verb.reflexive_only) and se else False

	verb.count += 1
	verb.save()
	verb.construct_conjugations()
	table = Table(verb, gender, reflexive)
	return render(request, 'conjugation/table.html', {
		'v': verb,
		'reflexive': reflexive,
		'feminin': feminin,
		'table': table,
		'forms_count': verb.template.forms_count,
		'forms_range': list(range(1, verb.template.forms_count + 1))
	})


def switch_keyboard_layout(s: str):
	for n in range(LAYOUT_EN.__len__()):
		s = s.replace(LAYOUT_RU[n], LAYOUT_EN[n])
	return s


def get_autocomplete_list(request):
	list_len = 50
	_term = request.GET['term'].lower()
	term = unidecode(_term)

	if term[:3] == 'se ' or term[:2] == "s'":
		verb_class = ReflexiveVerb
	else:
		verb_class = Verb
	q_startswith = verb_class.objects.filter(infinitive_no_accents__startswith=term)

	if q_startswith.__len__() == 0:
		term = switch_keyboard_layout(_term)
		q_startswith = verb_class.objects.filter(infinitive_no_accents__startswith=term)

	if q_startswith.__len__() < list_len:
		q_contains = verb_class.objects.filter(infinitive_no_accents__contains=term).difference(q_startswith)
		q = list(q_startswith) + list(q_contains)
	else:
		q = q_startswith

	autocomplete_list = []
	term_len = term.__len__()
	for v in q[0:list_len]:
		if not isinstance(v, ReflexiveVerb) and v.reflexive_only:
			v = v.reflexiveverb
		pos_start = v.infinitive_no_accents.find(term)
		pos_end = pos_start + term_len
		html = v.infinitive[0:pos_start] + '<b>' + v.infinitive[pos_start:pos_end] + '</b>' + v.infinitive[pos_end:]

		autocomplete_list.append(
			dict(url=v.get_absolute_url(), verb=v.infinitive, html=html))
	return JsonResponse(autocomplete_list, safe=False)


class Table:
	def __init__(self, v: Verb, gender: int, reflexive: bool):
		"""
		:param v: Verb object
		:param gender: -1 if feminine 0 if masculine
		:param reflexive: True|False
		"""
		self.v = v
		self.t = v.template
		self.moods = self.get_moods_list(gender, reflexive)

	def get_moods_list(self, gender, reflexive):
		moods = []
		for mood_name in FORMULAS.keys():
			mood = Mood(self.v, mood_name, gender, reflexive)
			moods.append(mood)
		return moods

	def all_polly(self):
		keys = list(filter(None, [tense.key if not tense.is_empty() else None for mood in self.moods for tense in mood.tenses]))
		polly_filter = Q()
		for key in keys:
			polly_filter = polly_filter | Q(key=key)
		query = PollyAudio.objects.filter(polly_filter)
		if len(query) < len(keys):
			return False
		return True

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
	_key = None

	def __init__(self, v: Verb=None, mood_name=None, tense_name=None, gender: int=None, reflexive: bool=None, key=None):
		if key:
			verb_infinitive_no_accents, mood_name, tense_name, gender, reflexive = key.split('_')
			v, gender, reflexive = Verb.objects.get(infinitive_no_accents=verb_infinitive_no_accents), int(gender), False if reflexive in ('False', 'None') else True
		self.v = v
		self.tense_name = tense_name
		self.mood_name = mood_name
		self.gender = gender
		self.reflexive = reflexive
		self.name = TEMPLATE_NAME[tense_name]
		self.persons = self.get_persons_list()

	@property
	def key(self):
		if not self._key:
			self._key = self.v.infinitive_no_accents + '_' + self.mood_name + '_' + self.tense_name + '_' + self.gender.__str__() + '_' + self.reflexive.__str__()
		return self._key

	def is_empty(self):
		return all(map(lambda a: a.part_0 == '-', self.persons))

	def get_persons_list(self):
		if self.v.deffective:
			if self.v.deffective.has_mood_tense(self.mood_name, self.tense_name):
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

	def get_polly_ssml(self):
		ssml = '<speak>{mood} {tense}.<prosody rate="slow">'.format(
			infinitive=self.v.infinitive,
			mood=TEMPLATE_NAME[self.mood_name] if (self.mood_name, self.tense_name) not in POLLY_EMPTY_MOOD_NAMES else '',
			tense=TEMPLATE_NAME[self.tense_name])
		for n, person in enumerate(self.persons):
			if person.part_0 == '-':
				continue
			ssml += sub('<.*?>', '', '{part0}{part1}{part2}'.format(part0=person.part_0, part1=person.forms[0], part2=person.part_2))
			if n == 2:
				ssml += '. '
			else:
				ssml += ', '
		ssml = ssml[0:-1] + '.'
		ssml += '</prosody></speak>'
		return ssml


class Person:

	def __init__(self, v: Verb, mood_name: str, tense_name: str, person_name: str, gender: int, reflexive: bool, empty=False):
		self.v = v
		self.mood_name = mood_name
		self.tense_name = tense_name
		self.person_name = person_name

		pronoun = -1 if v.infnitive_first_letter_is_vowel() else 0
		etre = 2 if not self.v.conjugated_with_avoir and self.v.conjugated_with_etre else 1
		if self.v.is_impersonal and self.person_name != "person_III_S":
			self.all_empty()
		elif empty:
			self.all_empty()
		else:
			self.part_0, self.forms, self.part_2 = self.get_parts(etre, 0, gender, pronoun, reflexive)
		if not isinstance(self.forms, list):
			self.forms = [self.forms]

	def more_than_one(self):
		if len(self.forms) > 1:
			return True
		else:
			return False

	def all_empty(self):
		self.part_0, self.forms, self.part_2 = '-', '', ''

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
		if path_to_conjugation is None:
			return '-', '', ''
		verb_forms = self.v.conjugations[path_to_conjugation[0]][path_to_conjugation[1]][int(path_to_conjugation[2])]
		if verb_forms is None:
			return '-', '', ''

		if isinstance(verb_forms, list):
			if verb_forms[0][0] == '<':
				pronoun = -1 if verb_forms[0][3] in VOWELS_LIST and not self.v.aspirate_h else 0
			else:
				pronoun = -1 if verb_forms[0][0] in VOWELS_LIST and not self.v.aspirate_h else 0
		else:
			if verb_forms[0] == '<':
				pronoun = -1 if verb_forms[3] in VOWELS_LIST and not self.v.aspirate_h else 0
			else:
				pronoun = -1 if verb_forms[0] in VOWELS_LIST and not self.v.aspirate_h else 0

		return parts[0][gender][pronoun], verb_forms, parts[2][gender][pronoun]

	def __str__(self):
		return self.person_name
