from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from unidecode import unidecode
from .polly import TEXT_TYPES, LANGUAGE_CODES, OUTPUT_FORMATS, SAMPLE_RATES, VOICE_IDS, TASK_STATUSES, PARAMS

VOWELS_LIST = ['a', 'ê', 'é', 'è', 'h', 'e', 'â', 'i', 'o', 'ô', 'u', 'w', 'y', 'œ', ]

FEMININE = -1
MASCULINE = 0


class PollyAudio(models.Model):
	key = models.CharField(max_length=64, primary_key=True)
	polly = models.ForeignKey('polly.PollyTask', null=True)


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
	verb = models.OneToOneField('conjugation.Verb', primary_key=True)
	fr_word = models.CharField(max_length=100, blank=True)
	fr_tag = models.OneToOneField('FrTag', null=True)
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
	translation = models.ForeignKey('Translation', related_name='parent')
	child = models.ForeignKey('Translation', related_name='child')
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
	text_fr = models.CharField(max_length=100000, default='')


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
	_conjugations = None

	count = models.IntegerField(default=0)
	infinitive = models.CharField(max_length=100)
	infinitive_no_accents = models.CharField(max_length=100, default='')
	template = models.ForeignKey(Template)
	aspirate_h = models.BooleanField(default=False)
	maison = models.BooleanField(default=False)

	homonym = models.IntegerField(null=True, default=None)

	reflexive_only = models.BooleanField(default=False)

	is_defective = models.BooleanField(default=False)
	deffective = models.ForeignKey('DeffectivePattern', null=True, on_delete=models.SET_NULL)

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

	group_no = models.IntegerField(default=1)
	group_str = models.CharField(default="", max_length=256)
	id_regle = models.IntegerField(default=200)

	regle = models.ForeignKey(Regle, on_delete=models.SET_NULL, blank=True, null=True)

	audio_url = models.URLField(default=None, null=True)

	main_part = models.CharField(max_length=64)
	main_part_no_accents = models.CharField(max_length=64)

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
		return reverse('conjugation:verb', kwargs=dict(verb=self.infinitive_no_accents))

	def url(self):
		return self.get_absolute_url()

	def __str__(self):
		return self.infinitive

	def get_main_part(self):
		return self.infinitive.rsplit(self.template.infinitive_ending(), 1)[0]

	def get_infinitive_no_accents(self):
		return unidecode(self.infinitive)

	def feminin_url(self):
		return reverse('conjugation:verb', kwargs=dict(femenin='feminin_', verb=self.infinitive_no_accents, se=None))

	def se_url(self):
		return reverse('conjugation:verb', kwargs=dict(femenin=None, verb=self.infinitive_no_accents, se='se_'))

	def feminin_se_url(self):
		return reverse('conjugation:verb', kwargs=dict(femenin='feminin_', verb=self.infinitive_no_accents, se='se_'))

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
			for i in range(1, 3):
				self._conjugations['participle']['past-participle'][i] = self._conjugations['participle']['past-participle'][0]

	@property
	def conjugations(self):
		if self._conjugations is None:
			self.construct_conjugations()
		return self._conjugations

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



class ReflexiveVerb(models.Model):
	verb = models.OneToOneField(Verb, on_delete=models.CASCADE, primary_key=True)
	infinitive = models.CharField(max_length=100)
	infinitive_no_accents = models.CharField(max_length=100)

	is_deffective = models.BooleanField(default=False)
	deffective = models.ForeignKey('DeffectivePattern', null=True, on_delete=models.SET_NULL)

	is_impersonal = models.BooleanField(default=False)

	def is_short(self):
		if self.verb.infnitive_first_letter_is_vowel():
			return True
		else:
			return False

	def create_no_accents(self):
		self.infinitive_no_accents = unidecode(self.infinitive)

	def url(self):
		return self.get_absolute_url()

	def get_absolute_url(self):
		if self.is_short():
			particule = "s_"
		else:
			particule = "se_"
		return reverse('conjugation:verb', kwargs=dict(se=particule, verb=self.verb.infinitive_no_accents))

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
