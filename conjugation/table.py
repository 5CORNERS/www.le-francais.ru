import re
from re import sub

from django.db.models import Q

from conjugation.consts import POLLY_EMPTY_MOOD_NAMES, VOWELS_LIST, \
	TEMPLATE_NAME, SHORT_LIST, ETRE, AVOIR, VOWEL, NOT_VOWEL, GENDER_MASCULINE, VOICE_ACTIVE, VOICE_REFLEXIVE, \
	VOICE_PASSIVE, GENDER_FEMININE, KEY_TO_PERSON, KEY_TO_MOOD_TENSE, KEY_TO_SWITCH
from conjugation.models import Verb, PollyAudio, Except
from conjugation.furmulas import *


class Table:
	def __init__(
			self, v: Verb,
			gender: int,
			reflexive: bool = False,
			negative: bool = False,
			question: bool = False,
			passive: bool = False,
			pronoun: bool = False,
	):
		"""
		:param v: Verb object
		:param gender: -1 if feminine 0 if masculine
		:param reflexive: True|False
		"""
		self.v = v
		self.t = v.template
		self.verb_exceptions = list(v.get_exceptions())
		self.moods = self.get_moods_list(gender, reflexive, negative, question, passive, pronoun, self.verb_exceptions)

	def get_moods_list(self, gender, reflexive, negative, question, passive, pronoun, exeptions):
		moods = []
		for mood_name in FORMULAS.keys():
			mood = Mood(self.v, mood_name, gender, reflexive, negative, question, passive, pronoun, exeptions)
			moods.append(mood)
		return moods

	def all_polly(self):
		return True
		# keys = list(filter(None, [tense.key if not tense.is_empty() else None for mood in self.moods for tense in mood.tenses]))
		# polly_filter = Q()
		# for key in keys:
		# 	polly_filter = polly_filter | Q(key=key)
		# query = PollyAudio.objects.filter(polly_filter)
		# if len(query) < len(keys):
		# 	return False
		# return True

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
					if tense.tense_name == tense_name or f'{mood.mood_name}-{tense.tense_name}' == tense_name or tense.tense_name in tense_name.split('-'):
						person = tense.persons[person]
						conjugation = f'{person.part_0}{person.forms[form]}{person.part_2}'
						return conjugation if conjugation != '-' else None
		return None


	def to_dict(self):
		d = {}
		for mood in self.moods:
			d[mood.mood_name] = mood.to_dict()
		return d


def get_table(verb: Verb, negative: bool = False, question: bool = False, voice: str = VOICE_ACTIVE, pronoun: bool = False,
			  gender: str = GENDER_MASCULINE) -> Table:
	return Table(
		verb,
		gender='m' if gender == GENDER_MASCULINE else 'f',
		reflexive=True if voice == VOICE_REFLEXIVE else False,
		negative=negative,
		question=question,
		passive=True if voice == VOICE_PASSIVE else False,
		pronoun=pronoun
	)



class Mood:
	def __init__(self, v, mood_name, gender: str, reflexive: bool, negative: bool, question: bool,
				 passive: bool, pronoun: bool, verb_exceptions):
		self.name = TEMPLATE_NAME[mood_name]
		self.v = v
		self.mood_name = mood_name
		self.verb_exceptions= verb_exceptions
		self.tenses = self.get_tenses_list(gender, reflexive, negative, question, passive, pronoun, verb_exceptions)

	def get_tenses_list(self, gender, reflexive, negative, question, passive, pronoun, exceptions):
		tenses = []
		mood_dict = FORMULAS[self.mood_name]
		for tense_name in mood_dict.keys():
			tense = Tense(self.v, self.mood_name, tense_name, gender, reflexive, negative, question, passive, pronoun, exceptions)
			tenses.append(tense)
		return tenses

	def __str__(self):
		return self.mood_name

	def to_dict(self):
		d = {}
		for tense in self.tenses:
			d[tense.tense_name] = tense.to_dict()
		return d


class Tense:
	_key = None

	def __init__(self, v: Verb = None, mood_name=None, tense_name=None, gender: str = GENDER_MASCULINE,
				 reflexive: bool = None, negative: bool = None, question: bool = None,
				 passive: bool = None, pronoun: bool = None, verb_exceptions=None, key=None):
		if key:
			verb_infinitive_no_accents, mood_name, tense_name, gender, reflexive, negative, question, passive, pronoun, homonym = key.split('_')
			reflexive, negative, question, passive, pronoun, homonym = reflexive == 'True', negative == 'True', question == 'True', passive == 'True', pronoun == 'True', None if homonym == 'None' else int(homonym)
			v = Verb.objects.get(infinitive_no_accents=verb_infinitive_no_accents, homonym=homonym)
		self.v = v
		self.verb_exceptions = verb_exceptions
		self.tense_name = tense_name
		self.mood_name = mood_name
		self.gender = gender
		self.reflexive = reflexive
		self.negative = negative
		self.question = question
		self.passive = passive
		self.pronoun = pronoun
		self.name = TEMPLATE_NAME[tense_name]
		self.persons = self.get_persons_list()

	@property
	def key(self):
		if not self._key:
			self._key = f'{self.v.infinitive_no_accents}_{self.mood_name}_{self.tense_name}_{self.gender}_{self.reflexive}_{self.negative}_{self.question}_{self.passive}_{self.pronoun}_{self.v.homonym}'
		return self._key

	def is_empty(self):
		return all(map(lambda a: a.part_0 == '-', self.persons))

	def get_persons_list(self):
		# if self.v.deffective:
		# 	if self.v.deffective.has_mood_tense(self.mood_name, self.tense_name):
		# 		return self.get_empty_persons_list()
		persons = []
		tense_dict = FORMULAS[self.mood_name][self.tense_name]
		for person_name in tense_dict[1].keys():
			person = Person(self.v, self.mood_name, self.tense_name, person_name, self.gender,
							self.reflexive, self.negative, self.question, self.passive, self.pronoun, self.verb_exceptions)
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
		ssml = ssml[0:-2] + '.'
		ssml += '</prosody></speak>'
		return ssml

	def to_dict(self):
		d = []
		if self.mood_name == 'participle' and self.tense_name == 'past':
			self.gender = GENDER_MASCULINE
			m_persons = self.get_persons_list()
			self.gender = GENDER_FEMININE
			f_persons = self.get_persons_list()
			self.persons = [m_persons[0], f_persons[0], m_persons[1], f_persons[1], m_persons[2]]
		for person in self.persons:
			d.append(person.to_dict())
		return d


import json
FORMULAS_JSON = json.load(open('conjugation/formulas.json'))

def switches_to_key(reflexive, negative, question, passive, pronoun):
	keys = []
	if question:
		keys.append('QUESTION')
	if reflexive and not pronoun:
		keys.append('REFLEXIVE')
	elif pronoun:
		keys.append('S-EN')
	if negative:
		keys.append('NEGATIVE')
	if passive:
		keys.append('PASSIVE')
	return '_'.join(keys)

def get_formula(reflexive, negative, question, passive, pronoun):
	key = switches_to_key(reflexive, negative, question, passive, pronoun)
	return FORMULAS_JSON[key]


class Person:

	def __init__(self, v: Verb, mood_name: str, tense_name: str, person_name: str, gender: str,
				 reflexive: bool = False, negative: bool = False, question: bool = False, passive: bool = False,
				 pronoun: bool = False, verb_exceptions=None, empty=False):
		self._verb_exceptions = verb_exceptions
		self.v = v
		self.mood_name = mood_name
		self.tense_name = tense_name
		self.person_name = person_name
		self.gender = gender
		self.reflexive = reflexive
		self.negative = negative
		self.question = question
		self.passive = passive
		self.pronoun = pronoun

		vowel_0 = -1 if v.infnitive_first_letter_is_vowel() else 0
		if not self.v.conjugated_with_avoir or self.reflexive or self.v.is_etre_verb:
			etre_or_avoir = ETRE
		else:
			etre_or_avoir = AVOIR
		if self.v.is_impersonal and (
				self.person_name != "person_III_S" and not (self.person_name == 'singular' and gender == 'm') and self.person_name != 'compose' and self.mood_name != 'infinitive' and self.mood_name != 'gerund'
		):
			self.all_empty()
		elif empty:
			self.all_empty()
		else:
			self.part_0, self.forms, self.part_2 = self.get_parts(etre_or_avoir, 0, gender, vowel_0, reflexive, negative, question, passive, pronoun)
		if not isinstance(self.forms, list):
			self.forms = [self.forms]
		self.replace()

	@property
	def more_than_one(self):
		if len(self.forms) > 1:
			return True
		else:
			return False

	def all_empty(self):
		self.part_0, self.forms, self.part_2 = '-', '', ''

	def has_exceptions(self):
		if self.verb_exceptions:
			return True
		return False

	def get_parts(self, etre, switch, gender, vowel_0, reflexive, negative, question, passive, pronoun):

		formula = get_formula(reflexive, negative, question, passive, pronoun)
		person_formula = formula[self.mood_name][self.tense_name][etre][self.person_name]
		verb_key = person_formula['verb_part'][gender]
		if self.verb_exceptions:
			exception = self.verb_exceptions[-1]
			if verb_key is None and exception.override_blank or verb_key is not None:
				if exception.conjugation_override:
					verb_key = exception.conjugation_override
				if exception.blank:
					verb_key = None
		if verb_key is None:
			return '-', '', ''
		t_mood, t_tense, t_person = globals()[verb_key]
		verb_forms = self.v.conjugations[t_mood][t_tense][int(t_person)]
		if verb_forms is None:
			return '-', '', ''
		if isinstance(verb_forms, list):
			verb_forms = verb_forms.copy()
			verb_form:str = str(verb_forms[0])
		else:
			verb_form:str = str(verb_forms)

		for r in ['<b>', '</b>', '<i>', '</i>']:
			verb_form = verb_form.replace(r, '')

		if verb_form[0] in VOWELS_LIST and not self.v.aspirate_h:
			first_char_is_vowel = VOWEL
		else:
			first_char_is_vowel = NOT_VOWEL

		if verb_form[-1] in VOWELS_LIST:
			last_char_is_vowel = VOWEL
		else:
			last_char_is_vowel = NOT_VOWEL

		part_1 = person_formula['part_1'][gender][first_char_is_vowel]
		part_2 = person_formula['part_2'][gender][last_char_is_vowel]

		if self.question and self.mood_name == 'indicative' and self.tense_name == 'present' and self.person_name=='person_I_S':
			if isinstance(verb_forms, list):
				for n, verb_form in enumerate(verb_forms):
					verb_forms[n] = re.sub('e(?=</b>$|</i>$|$)', 'é', verb_forms[n])
			else:
				verb_forms = re.sub('e(?=</b>$|</i>$|$)', 'é', verb_forms)
			if self.v.infinitive == 'pouvoir':
				verb_forms = verb_forms[1]

		return part_1, verb_forms, part_2

	def __str__(self):
		return self.person_name

	@property
	def verb_exceptions(self):
		if self._verb_exceptions is None:
			self._verb_exceptions = list(self.v.get_exceptions())
		r = []
		for exception in self._verb_exceptions:
			gender_condition = (self.gender == GENDER_MASCULINE and exception.male_gender) or (
					self.gender == GENDER_FEMININE and exception.feminine_gender)
			mood_tense_condition = getattr(exception, KEY_TO_MOOD_TENSE[f'{self.mood_name}_{self.tense_name}'])
			person_condition = getattr(exception, KEY_TO_PERSON[self.person_name])
			switch_condition = getattr(exception, KEY_TO_SWITCH[switches_to_key(self.reflexive, self.negative, self.question, self.passive, self.pronoun)])
			if gender_condition and mood_tense_condition and person_condition and switch_condition:
				r.append(exception)
		return r


	def replace(self):
		for exception in self.verb_exceptions:
			if exception.pattern_1:
				self.part_0 = re.sub(exception.pattern_1, exception.replace_to_1, self.part_0)
			if exception.pattern_2:
				self.part_2 = re.sub(exception.pattern_2, exception.replace_to_2, self.part_2)
			if exception.pattern_verb:
				for i, form in enumerate(self.forms):
					self.forms[i] = re.sub(exception.pattern_verb, exception.replace_to_verb, form)


	def to_dict(self):
		s = f'{self.part_0}{re.sub(r"<.*?>","", self.forms[0])}{self.part_2}'
		return s.replace('\xa0', ' ')
