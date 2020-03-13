from re import sub

from django.db.models import Q

from conjugation.consts import POLLY_EMPTY_MOOD_NAMES, VOWELS_LIST, \
	TEMPLATE_NAME, SHORT_LIST
from conjugation.models import Verb, PollyAudio
from conjugation.furmulas import FORMULAS, FORMULAS_PASSIVE, FORMULAS_PASSIVE_X


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

	def get_conjugation(self, mood_name, tense_name, person, form=0):
		"""
		Return string or None with the conjugation according to
		"""
		for mood in self.moods:
			if mood.mood_name == mood_name:
				for tense in mood.tenses:
					# FIXME: names in formulas and base should be the same
					if tense.tense_name == tense_name or f'{mood.mood_name}-{tense.tense_name}' == tense_name or tense_name.split('-')[-1] == tense.tense_name:
						person = tense.persons[person]
						return f'{person.part_0}{person.forms[form]}{person.part_2}'
		return None

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
