import re
from typing import List, Any, Tuple

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from unidecode import unidecode

from .consts import MOODS, TENSES, VOICE_REFLEXIVE, VOICE_PASSIVE, GENDER_FEMININE, GENDER_MASCULINE, VOICE_ACTIVE, \
	MOODS_TENSES, TEMPLATE_VERBS, PERSONS_LIST, VERB_TEMPLATE_NAMES, SWITCHES_CHOICES, ETRE, AVOIR
from polly.const import TEXT_TYPES, LANGUAGE_CODES, OUTPUT_FORMATS, SAMPLE_RATES, VOICE_IDS, TASK_STATUSES, PARAMS

VOWELS_LIST = ['a', 'ê', 'é', 'è', 'h', 'e', 'â', 'i', 'o', 'ô', 'u', 'w', 'y', 'œ', ]

FEMININE = -1
MASCULINE = 0


class PollyAudio(models.Model):
	key = models.CharField(max_length=128, primary_key=True)
	polly = models.ForeignKey('polly.PollyTask', null=True, on_delete=models.CASCADE)


TYPE_CHOICES = (
	('translation', 'Перевод'),
	('example', 'Пример использования'),
	('collocation', 'Устойчивое выражение'),
	('idiom', 'Идиоматическое выражение'),
	('none', 'Не выбрано')
)

STATUS_CHOICES = (
	('', ''),
	('', ''),
	('', ''),
)


class Translation(models.Model):
	verb = models.OneToOneField('conjugation.Verb', primary_key=True, on_delete=models.CASCADE)
	fr_word = models.CharField(max_length=100, blank=True)
	fr_tag = models.OneToOneField('FrTag', null=True, on_delete=models.CASCADE)
	ru_word = models.CharField(max_length=800, null=True, default=None)
	ru_tags = models.ManyToManyField('RuTag')
	type = models.CharField(choices=TYPE_CHOICES, max_length=10, null=True, default=None)
	status = models.CharField(choices=STATUS_CHOICES, max_length=10, null=True, default=None)
	order = models.IntegerField(help_text='Поле для сортировки', default=0, blank=True)

	class Meta:
		ordering = ['order', 'verb']

	comment = models.CharField(max_length=1000, null=True)

	children = models.ManyToManyField('self', through='ChildrenRelation', symmetrical=False)


class ChildrenRelation(models.Model):
	translation = models.ForeignKey('Translation', related_name='parent', on_delete=models.CASCADE)
	child = models.ForeignKey('Translation', related_name='child', on_delete=models.CASCADE)
	order = models.IntegerField()


class Tag(models.Model):
	tag = models.CharField(max_length=100)

	def __str__(self):
		return self.tag

	class Meta:
		abstract = True


class FrTag(Tag):
	pass


class RuTag(Tag):
	word_normalise = models.CharField(max_length=100)

	def save(self, *args, **kwargs):
		morph = pymorphy2.MorphAnalyzer()
		self.word_normalise = ''.join(morph.parse(word)[0].normal_form for word in self.tag.split())
		super(RuTag, self).save(*args, **kwargs)



class Regle(models.Model):
	text_rus = models.CharField(max_length=100000, default='')
	text_fr = models.CharField(max_length=100000, default='', blank=True)

	def __str__(self):
		verb = self.verb_set.order_by('-count').first()
		if verb:
			return verb.infinitive
		else:
			return 'Verb Not Found'


class Template(models.Model):
	name = models.CharField(max_length=200)
	data = JSONField(default={})
	new_data = JSONField(default={})
	second_form = models.BooleanField(default=False)
	no_red_end = models.BooleanField(default=False)
	forms_count = models.IntegerField(default=1)

	def infinitive_ending(self):
		return self.name.split(':')[1]

	def __str__(self):
		return self.name


class Verb(models.Model):
	def __init__(self, *args, **kwargs):
		super(Verb, self).__init__(*args, **kwargs)
		self._exceptions = None
		self._conjugations = None
		self._conjugations_no_html = None

	count = models.IntegerField(default=0)
	infinitive = models.CharField(max_length=100)
	infinitive_no_accents = models.CharField(max_length=100, default='')
	template = models.ForeignKey(Template, on_delete=models.PROTECT)
	aspirate_h = models.BooleanField(default=False)
	maison = models.BooleanField(default=False)

	homonym = models.IntegerField(null=True, default=None, blank=True)

	reflexive_only = models.BooleanField(default=False)
	can_be_pronoun = models.BooleanField(default=False)

	is_defective = models.BooleanField(default=False)
	deffective = models.ForeignKey('DeffectivePattern', null=True, on_delete=models.SET_NULL, blank=True)

	pp_invariable = models.BooleanField(default=False)

	masculin_only = models.BooleanField(default=False)
	has_passive = models.BooleanField(default=False)
	has_second_form = models.BooleanField(default=False)
	has_s_en = models.BooleanField(default=False)

	s_en = models.BooleanField(default=False)
	can_passive = models.BooleanField(default=False)
	can_feminin = models.BooleanField(default=False)
	can_reflexive = models.BooleanField(default=False)
	is_second_form = models.BooleanField(default=False)
	is_frequent = models.BooleanField(default=False)
	is_transitive = models.BooleanField(default=False)
	is_intransitive = models.BooleanField(default=False)
	is_pronominal = models.BooleanField(default=False)
	belgium = models.BooleanField(default=False)
	africa = models.BooleanField(default=False)
	conjugated_with_avoir = models.BooleanField(default=False)
	conjugated_with_etre = models.BooleanField(default=False)
	is_impersonal = models.BooleanField(default=False)
	book = models.BooleanField(default=False)
	is_rare = models.BooleanField(default=False)
	is_archaique = models.BooleanField(default=False)
	is_slang = models.BooleanField(default=False)

	is_etre_verb = models.BooleanField(default=False)

	group_no = models.IntegerField(default=1)
	group_str = models.CharField(default="", max_length=256)
	id_regle = models.IntegerField(default=200)

	regle = models.ForeignKey(Regle, on_delete=models.SET_NULL, blank=True, null=True)

	audio_url = models.URLField(default=None, null=True, blank=True)

	main_part = models.CharField(max_length=64)
	main_part_no_accents = models.CharField(max_length=64)

	html_sizes = JSONField(null=True, blank=True, default=dict)

	@property
	def can_be_active(self):
		return not self.reflexive_only

	def employs(self):
		s = ""
		s += '<b>' + self.infinitive + "</b> — "
		s += 'дефективный ' if self.is_defective else ''
		s += 'дефективный безличный ' if self.is_impersonal else ''
		s += '«книжный» (редко употребляемый в устной речи) ' if self.book else ''
		s += 'глагол <b>' + str(self.group_no) + '-й группы</b>, '
		s += 'с h придыхательной в первой букве, ' if self.aspirate_h else ''
		s += 'частоупотребимый, ' if self.is_frequent else ''
		s += 'непереходный, ' if self.is_intransitive and not self.is_transitive else ''
		s += 'переходный, ' if self.is_transitive and not self.is_intransitive else ''
		s += 'может быть как переходным, так и непереходным, ' if self.is_intransitive and self.is_transitive else ''
		s += 'в составных временах спрягается со вспомогательным глаголом <b>avoir</b>, ' if self.conjugated_with_avoir and not self.conjugated_with_etre else ''
		s += 'в составных временах спрягается со вспомогательным глаголом <span title="Это откроет вам глаза" class="arnaud-comment" data-container="body" data-html="true" data-content="Почему некоторые глаголы спрягаются с ÊTRE — этому есть <a href=\'/oh-la-la/conjugue_avec_etre/?utm_campaign=conjugeur&utm_medium=button&utm_source=%C3%8ATRE\'>простое и изящное объяснение</a>. :)" data-placement="top" data-toggle="popover"><b>être</b></span>, ' if self.conjugated_with_etre and not self.conjugated_with_avoir else ''
		s += 'в составных временах спрягается как со вспомогательным глаголом <span title="Это откроет вам глаза" class="arnaud-comment" data-container="body" data-html="true" data-content="Почему некоторые глаголы спрягаются с ÊTRE — этому есть <a href=\'/oh-la-la/conjugue_avec_etre/?utm_campaign=conjugeur&utm_medium=button&utm_source=%C3%8ATRE\'>простое и изящное объяснение</a>. :)" data-placement="top" data-toggle="popover"><b>être</b></span>, так и с глаголом <b>avoir</b> — в зависимости от наличия прямого дополнения, ' if self.conjugated_with_avoir and self.conjugated_with_etre else ''
		s += 'имеет возвратную форму, ' if not self.reflexive_only and self.is_pronominal else ''
		s += 'существует только в возвратной форме, ' if self.reflexive_only else ''
		# s += 'имеет локальное хождение в Квебеке, ' if self.canada else ''
		s += 'имеет локальное хождение в Бельгии, ' if self.belgium else ''
		s += 'имеет локальное хождение в африканских странах, ' if self.africa else ''
		s += 'крайне редко употребим, ' if self.is_rare else ''
		s += 'устаревший, ' if self.is_archaique else ''
		s += 'используется, как слэнг, ' if self.is_slang else ''
		s += 'начинается с h придыхательного, ' if self.aspirate_h else ''
		s += 'причастие прошедшего времени <span style="color:#f28b1a"><b>(sic!)</b></span> остается неизменным в женском роде и во множественном числе, ' if self.pp_invariable else ''
		s = s[:-2] + '.'
		return s

	def get_absolute_url(self):
		return reverse('conjugation:verb', kwargs=dict(verb=self.infinitive_no_accents, homonym='_2' if self.homonym == 2 else ''))

	def get_url(self, negative=False, question=False, voice=VOICE_ACTIVE, pronoun=False, gender=GENDER_MASCULINE):
		url_kwargs = dict(
			feminin='', question='', negative='', passive='', reflexive='',
			pronoun='', verb=self.infinitive_no_accents, homonym='_2' if self.homonym == 2 else ''
		)
		if voice == VOICE_REFLEXIVE:
			if pronoun:
				url_kwargs['pronoun'] = 's-en_'
			else:
				url_kwargs['reflexive'] = 'se_'
		elif voice == VOICE_PASSIVE:
			url_kwargs['passive'] = '_voix-passive'

		if negative:
			url_kwargs['negative'] = '_negation'
		if question:
			url_kwargs['question'] = '_question'
		if gender == GENDER_FEMININE:
			url_kwargs['feminin'] = '_feminin'

		return reverse('conjugation:verb', kwargs=url_kwargs)

	def __str__(self):
		return self.infinitive

	def get_main_part(self):
		return self.infinitive.rsplit(self.template.infinitive_ending(), 1)[0]

	def get_infinitive_no_accents(self):
		return unidecode(self.infinitive)

	def feminin_url(self):
		return reverse('conjugation:verb', kwargs=dict(femenin='_feminin', verb=self.infinitive_no_accents, se=None, homonym='_2' if self.homonym == 2 else ''))

	def se_url(self):
		return reverse('conjugation:verb', kwargs=dict(femenin=None, verb=self.infinitive_no_accents, se='se_', homonym='_2' if self.homonym == 2 else ''))

	def feminin_se_url(self):
		return reverse('conjugation:verb', kwargs=dict(femenin='_feminin', verb=self.infinitive_no_accents, se='se_', homonym='_2' if self.homonym == 2 else ''))

	def infnitive_first_letter_is_vowel(self):
		return True if self.infinitive[0] in VOWELS_LIST and not self.aspirate_h else False

	def construct_conjugations(self):
		self._conjugations = {}
		for mood in self.template.new_data.keys():
			self._conjugations[mood] = {}
			for tense in self.template.new_data[mood].keys():
				self._conjugations[mood][tense] = [None] * 6
				for person, i in enumerate(self.template.new_data[mood][tense]['p']):
					endings = self.template.new_data[mood][tense]['p'][person]['i']
					if endings == None:
						pass
					elif isinstance(endings, list):
						forms = []
						for ending in endings:
							forms.append(self.main_part + ending)
						self._conjugations[mood][tense][person] = forms
					else:
						self._conjugations[mood][tense][person] = self.main_part + endings
		if self.pp_invariable:
			for i in range(1, 4):
				self._conjugations['participle']['past-participle'][i] = self._conjugations['participle']['past-participle'][0]

	@property
	def conjugations(self):
		if self._conjugations is None:
			self.construct_conjugations()
		return self._conjugations

	@property
	def conjugations_no_html(self):
		if self._conjugations_no_html is None:
			d = {}
			cleanr = re.compile('<.*?>')
			for mood in self.conjugations.keys():
				d[mood] = {}
				for tense in self.conjugations[mood].keys():
					d[mood][tense] = []
					for i, person in enumerate(self.conjugations[mood][tense]):
						if person is None:
							d[mood][tense].append(None)
							continue
						if isinstance(person, list):
							d[mood][tense].append([])
							for j, form in enumerate(person):
								d[mood][tense][i].append(re.sub(cleanr, '', form))
						else:
							d[mood][tense].append(re.sub(cleanr, '', person))
			self._conjugations_no_html = d
		return self._conjugations_no_html


	def find_form(self, f):
		f = unidecode(f)
		for mood, tense, person, form, n in self:
			if form and unidecode(form) == f:
				return mood, tense, form, n
		return None

	def find_forms(self, s, exact=False) -> list:
		"""
		Finds all forms which starts with the search string and returns
		list of tuples containing form itself and names of the mood and
		tense of the form
		:param exact: if True find only exact match forms
		:type s: str
		:param s: search string
		:rtype: List[Tuple[str, str, str, int, int]]
		:return: list of tuples (form, mood, tense, person, n)
			WHERE
			str form is founded form of the verb
			str mood is name of the mood
			str tense is name of the tense
			int person is name of the person
			int n is number of form or None
		"""
		forms: List[Tuple[str, str, str, str, int]] = []
		for mood, tense, person, form, n in self:
			if form and ((
				not exact and unidecode(form).startswith(unidecode(s))) or (
				exact and unidecode(form) == unidecode(s)
			)):
				forms.append((form, mood, tense, person, n))
		forms.sort(key=lambda x: (
		index_tuple(MOODS, x[1]), index_tuple(TENSES, x[2])))
		return forms


	def get_all(self):
		result = []

		genders = (MASCULINE, FEMININE)
		if self.masculin_only:
			genders = (MASCULINE, )

		if self.can_reflexive:
			refs = (False, True)
		elif self.reflexive_only:
			refs = (True, )
		else:
			refs = (False, )

		for gender in genders:
			for reflexive in refs:
				result.append((self, gender, reflexive))
		return result

	@property
	def forms_html(self):
		return self.__iter__(True)

	@property
	def forms(self):
		return self.__iter__(False)

	def __iter__(self, html=False):
		from .utils import flatten
		iter_list = []
		mood_tenses = flatten(self.conjugations_no_html).keys()
		for mood_tense in mood_tenses:
			mood, tense = mood_tense.split('_')
			if html:
				persons = self.conjugations[mood][tense]
			else:
				persons = self.conjugations_no_html[mood][tense]
			for i, person in enumerate(persons):
				if isinstance(person, list):
					for j, form in enumerate(person):
						iter_list.append((mood, tense, i, form, j))
				else:
					iter_list.append((mood, tense, i, person, None))
		return iter(iter_list)

	def get_exceptions(self):
		if self._exceptions is None:
			self._exceptions = list(self.exceptions.all())
		return self._exceptions

	def conjugates_with(self):
		if self.is_etre_verb or not self.conjugated_with_avoir:
			return ETRE
		return AVOIR

	def get_available_switches_configuration(self):
		result = []
		for switch_key, switch in SWITCHES_CHOICES:
			reflexive = 'REFLEXIVE' in switch
			pronoun = 'S-EN' in switch
			passive = 'PASSIVE' in switch
			if self.reflexive_only and not (reflexive or pronoun):
				continue
			elif reflexive and not pronoun and not self.can_reflexive and not self.reflexive_only:
				continue
			elif not (self.reflexive_only or self.can_reflexive or self.can_be_pronoun) and reflexive:
				continue
			elif (reflexive == "se_" and self.reflexiveverb.is_short()) or (
					reflexive == "s_" and not self.reflexiveverb.is_short()):
				continue

			if not self.can_passive and passive:
				continue
			if not self.can_be_pronoun and pronoun:
				continue
			result.append((switch_key, switch))
		return result

	def get_all_urls(self):
		available_switches = self.get_available_switches_configuration()
		urls = []
		for switch, k in available_switches:
			is_active='active' in switch
			is_pronominal = 'pronominal' in switch and not '_en' in switch
			is_voix_passive = 'voix_passive' in switch
			is_question = 'question' in switch
			is_negation = 'negation' in switch
			is_pronominal_en = 'pronominal_en' in switch
			if is_active:
				voice = VOICE_ACTIVE
			elif is_pronominal or is_pronominal_en:
				voice = VOICE_REFLEXIVE
			else:
				voice = VOICE_PASSIVE
			genders = [GENDER_MASCULINE]
			if self.can_feminin:
				genders.append(GENDER_FEMININE)
			for gender in genders:
				urls.append(self.get_url(
					voice=voice,
					pronoun=is_pronominal_en,
					negative=is_negation,
					question=is_question,
					gender=gender
				))
		return urls


class Except(models.Model):
	name = models.CharField(default='Exception', max_length=100)
	blank = models.BooleanField(default=False, verbose_name='Empty')
	override_blank = models.BooleanField(default=False, verbose_name='Override blank', help_text='If true, exception will override blank strings in the formula, this could lead to results like "None<verb>None"')
	etre = models.CharField(max_length=10, verbose_name='"Etre" or "Avoir"', choices=[(ETRE, 'Etre'),(AVOIR,'Avoir')], null=True, blank=True)
	pattern_1 = models.CharField(max_length=100, verbose_name='Regex Before', null=True, blank=True)
	replace_to_1 = models.CharField(max_length=100, verbose_name='Replace To Before', null=True, blank=True)
	pattern_2 = models.CharField(max_length=100, verbose_name='Regex After', null=True, blank=True)
	replace_to_2 = models.CharField(max_length=100, verbose_name='Replace To After', null=True, blank=True)
	pattern_verb = models.CharField(max_length=100, verbose_name='Regex Verb', null=True, blank=True)
	replace_to_verb = models.CharField(max_length=100, verbose_name='Replace To Verb', null=True, blank=True)
	conjugation_override = models.CharField(max_length=64, choices=VERB_TEMPLATE_NAMES, null=True, blank=True)
	verbs = models.ManyToManyField('conjugation.Verb', related_name='exceptions')
	male_gender = models.BooleanField(default=True, blank=True)
	feminine_gender = models.BooleanField(default=True, blank=True)
	order = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f'{self.name}:{self.pk}'

for mood_tense, name in MOODS_TENSES:
	Except.add_to_class(mood_tense, models.BooleanField(verbose_name=name, default=False))

for persons, name in PERSONS_LIST:
	Except.add_to_class(persons, models.BooleanField(verbose_name=name, default=False))

for key, name in SWITCHES_CHOICES:
	Except.add_to_class(key, models.BooleanField(verbose_name=name, default=False))

class ReflexiveVerb(models.Model):
	verb = models.OneToOneField(Verb, on_delete=models.CASCADE, primary_key=True)
	infinitive = models.CharField(max_length=100)
	infinitive_no_accents = models.CharField(max_length=100)

	is_deffective = models.BooleanField(default=False)
	deffective = models.ForeignKey('DeffectivePattern', null=True, on_delete=models.SET_NULL)

	is_impersonal = models.BooleanField(default=False)

	@property
	def non_breakable_space_infinitive(self):
		return self.infinitive.replace(' ', '&nbsp;')

	def is_short(self):
		if self.verb.infnitive_first_letter_is_vowel():
			return True
		else:
			return False

	def create_no_accents(self):
		self.infinitive_no_accents = unidecode(self.infinitive)

	def get_absolute_url(self):
		if self.is_short():
			particule = "s_"
		else:
			particule = "se_"
		return reverse('conjugation:verb', kwargs=dict(reflexive=particule, verb=self.verb.infinitive_no_accents, homonym='_2' if self.verb.homonym else ''))

	def rename(self):
		self.infinitive = "s'" + self.verb.infinitive if self.verb.infnitive_first_letter_is_vowel() and not self.verb.aspirate_h else "se " + self.verb.infinitive
		self.create_no_accents()
		self.save()


class DeffectivePattern(models.Model):
	indicative_compose_past = models.BooleanField(default=False)
	indicative_anterieur_past = models.BooleanField(default=False)
	indicative_pluperfect = models.BooleanField(default=False)
	indicative_anterieur_future = models.BooleanField(default=False)
	subjunctive_past = models.BooleanField(default=False)
	subjunctive_pluperfect = models.BooleanField(default=False)
	conditional_past_first = models.BooleanField(default=False)
	conditional_past_second = models.BooleanField(default=False)
	imperative_past = models.BooleanField(default=False)
	infinitive_past = models.BooleanField(default=False)
	gerund_past = models.BooleanField(default=False)

	def has_mood_tense(self, mood_name, tense_name):
		mood_tense = unidecode(mood_name + '_' + tense_name.replace('-', '_'))
		try:
			if self.__getattribute__(mood_tense):
				return True
			else:
				return False
		except:
			return False


def index_tuple(l, value, index=0):
	"""
	Returns index of tuple in list of tuples, which [j] element is the same as s string
	:param index: index for searching tuples
	:param l: target list
	:param value: search string
	:return: index of tuple
	:rtype: int
	"""
	for pos, t in enumerate(l):
		if t[index] == value:
			return pos
	raise ValueError("list.index(x): x not in list")
