import re
import statistics
import string
from datetime import datetime
from urllib.parse import quote

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.utils.http import urlencode, urlquote
from regex import regex

from le_francais_dictionary.consts import GENRE_CHOICES, \
	PARTOFSPEECH_CHOICES, \
	PARTOFSPEECH_NOUN, GENRE_MASCULINE, GENRE_FEMININE, \
	GRAMMATICAL_NUMBER_CHOICES, PARTOFSPEECH_ADJECTIVE
from le_francais_dictionary.utils import sm2_response_quality, \
	sm2_next_repetition_date, format_text2speech, sm2_ef_q_mq
from polly import const as polly_const
from polly.models import PollyTask

from django.contrib.auth import get_user_model

User = get_user_model()


class Packet(models.Model):
	name = models.CharField(max_length=128)
	demo = models.BooleanField(default=False)
	lesson = models.ForeignKey('home.LessonPage',
	                           related_name='dictionary_packets', null=True)

	def __str__(self):
		return '{self.name}'.format(self=self)

	def to_dict(self, user=None) -> dict:
		"""
		:param user: user object
		:type user: User
		:returns: A dictionary of packet which can be safely turned into json
		:rtype: dict
		"""
		data = dict()
		data['pk'] = self.pk
		data['name'] = self.name
		data['lessonNumber'] = self.lesson.lesson_number
		data['demo'] = self.demo
		if user and user.is_authenticated:
			if self.lesson.payed(user):
				data['activated'] = True
				data['added'] = True
				data['wordsLearned'] = self.words_learned(user)
			else:
				data['activated'] = False
				data['added'] = False
				data['wordsLearned'] = None
		else:
			data['activated'] = None
			data['added'] = None
			data['wordsLearned'] = None
		data['wordsCount'] = self.word_set.all().count()
		return data

	def create_polly_task(self):
		for w in self.word_set.all():
			w.create_polly_task()

	@property
	def words_count(self):
		return self.word_set.all().count()

	def is_activated(self, user) -> bool:
		if self.lesson.payed(user):
			return True
		else:
			return False

	def _fully_voiced(self):
		if self.word_set.filter(Q(polly__isnull=True) | Q(
				wordtranslation__polly__isnull=True)).exists():
			return False
		else:
			return True
	_fully_voiced.boolean = True
	fully_voiced = property(_fully_voiced)

	def words_learned(self, user) -> int:
		return self.word_set.filter(
			Q(userdata__user=user, userdata__grade=1) | Q(
				userwordignore__user=user
			)).values(
			'word').distinct().__len__()


class UserPacket(models.Model):
	packet = models.ForeignKey(Packet)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)

	@property
	def words_learned(self) -> int:  # TODO
		return self.packet.word_set.filter(
			Q(userdata__user=self.user, userdata__grade=1)|Q(
				userwordignore__user=self.user
			)).values(
			'word').distinct().__len__()


class WordGroup(models.Model):
	pass


class UnifiedWord(models.Model):
	word = models.CharField(max_length=120)
	translation = models.CharField(max_length=120)
	definition_num = models.IntegerField(null=True, blank=True, default=None)
	group = models.ForeignKey('WordGroup', on_delete=models.CASCADE)
	word_polly_url = models.URLField(max_length=200, null=True, default=None)
	translation_polly_url = models.URLField(max_length=200, null=True,
	                                        default=None)

	@property
	def ru_filename(self):
		if self.translation_polly_url:
			return self.translation_polly_url.rsplit('/', 1)[-1]
		else:
			return None

	@property
	def fr_filename(self):
		if self.translation_polly_url:
			return self.word_polly_url.rsplit('/', 1)[-1]
		else:
			return None


class EmptyUni:
	word = None
	translation = None
	word_polly_url = None
	translation_polly_url = None
	ru_filename = None
	fr_filename = None


UNRELEVANT_STARTS = [
	'une ',
	'un ',
	'le ',
	'la ',
	'des ',
	'les ',
	'l\'',
]

UNRELEVANT_ENDS = [
	' + infinitive', ' + infinitif', ' + subjonctif', ' de', ' que', ' par', ' à',
	' pour', ' à quelque chose', ' de quelque chose',
	' quelqu\'un à quelque chose', ' à quelqu\'un', ' qch/qqn', ' qqn', ' qqn/qch',
	' qqn de+inf', ' de qch', ' qch à', ' qch', ' à qn de qch'
]

def del_ends(s):
	s = s.rstrip('!?., ')
	for end in UNRELEVANT_ENDS:
		if s.endswith(' ' + end):
			s.replace(' ' + end, '')
			s = del_ends(s)
	return s


class Word(models.Model):
	cd_id = models.IntegerField(
		verbose_name='Color Dictionary ID',
		primary_key=True)
	word = models.CharField(max_length=120, verbose_name='Word')
	word_ssml = models.CharField(max_length=200, null=True, default=None, blank=True)
	polly = models.ForeignKey(PollyTask, null=True, blank=True)
	_polly_url = models.URLField(max_length=200, null=True, default=None, blank=True)
	# TODO: must be moved to WordTranslation Model
	genre = models.CharField(choices=GENRE_CHOICES, max_length=10, null=True,
	                         verbose_name='Gender', blank=True)
	part_of_speech = models.CharField(choices=PARTOFSPEECH_CHOICES,
	                                  max_length=10, null=True,
	                                  verbose_name='Part of Speech', blank=True)
	plural = models.BooleanField(default=False, verbose_name='Plural', blank=True)
	grammatical_number = models.CharField(choices=GRAMMATICAL_NUMBER_CHOICES,
	                                      max_length=4, null=True, blank=True)
	packet = models.ForeignKey(Packet, null=True, default=None, blank=True)

	group = models.ForeignKey('WordGroup', on_delete=models.SET_NULL, null=True, blank=True)
	definition_num = models.IntegerField(null=True, blank=True, default=None)

	order = models.IntegerField(null=True, default=None)

	def __init__(self, *args, **kwargs):
		super(Word, self).__init__(*args, **kwargs)
		self._unrelated = None
		self._last_user_data = {}
		self._is_marked = {}
		self._repetitions_count = {}
		self._first_translation = None
		self._repetitions = {}

	def mistake_ratio(self, mistakes):
		word = self.word
		p1 = regex.compile(r"(?P<un>\L<unrelevants>)",
		                   unrelevants=[unr for unr in
		                                UNRELEVANT_STARTS + UNRELEVANT_ENDS])
		_s_word = regex.sub(p1, '(\g<un>)', word)
		_s_user = ''
		c = 0
		for i in range(mistakes):
			try:
				if word[c] == ' ':
					_s_user += ' '
					c += 1
				_s_user += word[c]
				c += 1
			except IndexError:
				break
		for i, char in enumerate(_s_word):
			if char in ['(', ')'] and len(_s_user) > i and _s_user[i]!=char:
				_s_user = _s_user[:i] + char + _s_user[i:]
		p2 = regex.compile(r"\(.+?(\)|$)")
		s_word = regex.sub(p2, '', _s_word)
		s_user = regex.sub(p2, '', _s_user)
		return len(s_user)/len(s_word)


	@property
	def real_len(self):
		s = self.word
		re.sub(r'', '', s)
		s = ''.join(
			s.translate(str.maketrans("()[]", "💲" * 4)).split('💲')[::2])
		s = del_ends(s)
		return len(s)

	@property
	def unrelated_mistakes(self):
		if self._unrelated is not None:
			return self._unrelated
		else:
			result = 0
		for u in UNRELEVANT_STARTS:
			if self.word.startswith(u):
				result = len(u)
				break
		self._unrelated = result
		return self.unrelated_mistakes


	@property
	def uni(self):
		if self.group:
			return self.group.unifiedword_set.get(definition_num__exact=self.definition_num)
		else:
			return EmptyUni()

	@property
	def filename(self):
		if self._polly_url:
			return self._polly_url.rsplit('/', 1)[-1]
		else:
			return None


	@property
	def polly_url(self):
		if not self._polly_url:
			return self.polly.url if self.polly else None
		else:
			return urlquote(self._polly_url, safe='/:')

	@property
	def first_translation(self):
		if self._first_translation is None:
			self._first_translation = self.wordtranslation_set.first()
		return self._first_translation

	def last_user_data(self, user):
		if not user.pk in self._last_user_data:
			self._last_user_data[user.pk] = self.userdata.filter(
				user=user).order_by('-datetime').first()
		return self._last_user_data[user.pk]

	def e_factor(self, user):
		if self.last_user_data(user):
			return self.last_user_data(user).e_factor
		else:
			return None

	def mean_quality(self, user):
		if self.last_user_data(user):
			return float(round(self.last_user_data(user).mean_quality * 2) / 2)
		else:
			return None

	def mean_quality_filter_value(self, user):
		q = self.mean_quality(user)
		if q is not None:
			return str(float(q)).replace('.', '@')
		else:
			return 'None'

	def repetition(self, user):
		if not user.pk in self._repetitions.keys():
			repetition = UserWordRepetition.objects.filter(
				user=user,
				word__group_id=self.group_id,
				word__definition_num=self.definition_num,
			).first()
			if repetition:
				self._repetitions[user.pk] = repetition
			else:
				self._repetitions[user.pk] = None
		return self._repetitions[user.pk]

	def get_repetition_date(self, user):
		try:
			return self.userwordrepetition_set.filter(user=user).repetition_date
		except:
			return None

	def repetitions_count(self, user):
		if not user.pk in self._repetitions_count.keys():
			try:
				self._repetitions_count[user.pk] = self.userwordrepetition_set.get(user=user).time or 0
			except:
				self._repetitions_count[user.pk] = None
		return self._repetitions_count[user.pk]
	def get_difficulty_5(self, user):
		if self.mean_quality(user):
			return 5 - self.mean_quality(user)
		else:
			return None

	def get_difficulty_10(self, user):
		if self.e_factor(user):
			return -((self.e_factor(user) - 1.3)*2 - 10)
		else:
			return None

	def get_difficulty_20(self, user):
		if self.e_factor(user):
			return -((self.e_factor(user) - 1.3)*4 - 20)
		else:
			return None

	def is_marked(self, user):
		if not user.pk in self._is_marked.keys():
			if self.userwordignore_set.filter(user=user).exists():
				self._is_marked[user.pk] = True
			else:
				self._is_marked[user.pk] = False
		return self._is_marked[user.pk]

	def to_dict(self, with_user=False, user=None):
		translation = self.first_translation
		if translation:
			translation_dict = translation.to_dict()
		else:
			translation_dict = None
		data = {
			'pk': self.pk,
			'word': self.word,
			'pollyUrl': self.polly_url,
			'gender': self.genre,
			'partOfSpeech': self.part_of_speech,
			'plural': self.plural,
			'grammaticalNumber': self.grammatical_number,
			'translation': translation_dict,
			'translations': [translation_dict],
			'packet': self.packet.pk,
			'userData': None,
		}
		if user and user.is_authenticated:
			repetition: UserWordRepetition = self.repetition(user)
			if repetition:
				repetition_time = repetition.time
				repetition_date = repetition.repetition_date
			else:
				repetition_time = None
				repetition_date = None
			data['userData'] = dict(
				nextRepetitionDate=repetition_date,
				repetitionTime=repetition_time,
			)
		return data

	def create_polly_task(self, local=None):
		if self.word_ssml:
			text = self.word_ssml
			text_type = polly_const.TEXT_TYPE_SSML
		else:
			text = format_text2speech(self.word)
			text_type = polly_const.TEXT_TYPE_TEXT
		if ((self.part_of_speech == PARTOFSPEECH_NOUN or
		     self.part_of_speech == PARTOFSPEECH_ADJECTIVE) and
				self.genre == GENRE_MASCULINE):
			voice_id = polly_const.VOICE_ID_MATHIEU
		elif ((self.part_of_speech == PARTOFSPEECH_NOUN or
		       self.part_of_speech == PARTOFSPEECH_ADJECTIVE) and
		      self.genre == GENRE_FEMININE):
			voice_id = polly_const.VOICE_ID_CELINE
		else:
			voice_id = polly_const.VOICE_ID_LEA
		polly_task = PollyTask(
			text=text,
			text_type=text_type,
			language_code=polly_const.LANGUAGE_CODE_FR,
			output_format=polly_const.OUTPUT_FORMAT_MP3,
			sample_rate=polly_const.SAMPLE_RATE_22050,
			voice_id=voice_id,
		)
		if local:
			import os
			stream = polly_task.get_audio_stream('polly-dictionaries/words-local/')
			path = 'le_francais_dictionary/local/fr_polly/'
			if (self.part_of_speech == PARTOFSPEECH_NOUN and
					self.genre == GENRE_MASCULINE):
				genre = 'm'
			elif (self.part_of_speech == PARTOFSPEECH_NOUN and
			      self.genre == GENRE_FEMININE):
				genre = 'f'
			else:
				genre = 'z'
			filename = local
			if os.path.exists(path+filename):
				return
			file = open(path + filename, 'wb')
			file.write(stream.read())
			file.close()
			import eyed3
			mp3 = eyed3.load(path + filename)
			mp3.tag.track_num = (str(self.cd_id), None)
			mp3.tag.title = str(self.word)
			mp3.tag.artist = str(voice_id)
			mp3.tag.album = 'Amazon Polly'
			mp3.tag.save()
			print(filename)
			# self.polly = 'https://files.le-francais.ru/dictionnaires/sound/' + filename
		else:
			polly_task.create_task('polly-dictionaries/words/', wait=False,
			                       save=True)
			self.polly = polly_task
			self.save()
		# for translation in self.wordtranslation_set.all():
		#     translation.create_polly_task()

	def __str__(self):
		return self.word


class WordTranslation(models.Model):
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	translation = models.CharField(max_length=120, null=False, blank=False)
	translations_ssml = models.CharField(max_length=200, null=True, default=None, blank=True)
	polly = models.ForeignKey(PollyTask, null=True, blank=True)
	_polly_url = models.URLField(null=True, default=None, blank=True)
	packet = models.ForeignKey('Packet', on_delete=models.CASCADE, null=True)

	@property
	def filename(self):
		if self._polly_url:
			return self._polly_url.rsplit('/', 1)[-1]
		else:
			return None

	@property
	def polly_url(self):
		if not self._polly_url:
			return self.polly.url if self.polly else None
		else:
			return urlquote(self._polly_url, safe='/:')

	@property
	def genre(self):
		if self.word:
			return self.word.genre
		else:
			return None

	@property
	def cd_id(self):
		if self.word:
			return self.word.cd_id
		else:
			return None

	def to_dict(self):
		return {
			'translation': self.translation,
			'pollyUrl': self.polly_url,
		}

	def create_polly_task(self):
		text = format_text2speech(self.translation)
		polly_task = PollyTask(
			text=text,
			text_type=polly_const.TEXT_TYPE_TEXT,
			language_code=polly_const.LANGUAGE_CODE_RU,
			output_format=polly_const.OUTPUT_FORMAT_MP3,
			sample_rate=polly_const.SAMPLE_RATE_22050,
			voice_id=polly_const.VOICE_ID_TATYANA,
		)
		polly_task.create_task('polly-dictionaries/translations/',
		                       wait=False,
		                       save=True)
		self.polly = polly_task
		self.save()

	def create_custom_audio(self):
		from os import getenv
		ftp_login = getenv('FTP_LOGIN', None)
		ftp_password = getenv('FTP_PASSWORD', None)


	def __str__(self):
		return self.translation


class UserWordIgnore(models.Model):
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class UserWordData(models.Model):
	word = models.ForeignKey(Word, related_name='userdata')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='flash_cards_data')
	datetime = models.DateTimeField(auto_now_add=True)
	grade = models.IntegerField()
	mistakes = models.IntegerField()

	def __init__(self, *args, **kwargs):
		super(UserWordData, self).__init__(*args, **kwargs)
		self._e_factor = -1
		self._quality = -1
		self._mean_quality = -1
		self._user_word_dataset = None


	@property
	def user_word_dataset(self):
		if self._user_word_dataset is None:
			self._user_word_dataset = list(UserWordData.objects.select_related('word', 'user').filter(
				word=self.word, user=self.user,
				datetime__lte=self.datetime).order_by('datetime'))
		return self._user_word_dataset

	@property
	def e_factor(self):
		if self._e_factor is -1:
			if self.grade:
				dataset = self.user_word_dataset
				self._e_factor, self._quality, self._mean_quality = sm2_ef_q_mq(dataset)
			else:
				self._e_factor, self._quality = None, None
		return self._e_factor

	@property
	def mean_quality(self):
		if self._mean_quality is -1:
			if self.grade:
				dataset = self.user_word_dataset
				self._e_factor, self._quality, self._mean_quality = sm2_ef_q_mq(
					dataset)
		return self._mean_quality

	@property
	def quality(self):
		if self._quality is -1:
			dataset = self.user_word_dataset
			self._e_factor, self._quality, self._mean_quality = sm2_ef_q_mq(dataset)
		return self._quality

	def get_e_factor(self):
		return self.e_factor

	def get_repetition_datetime(self):
		dataset = self.user_word_dataset
		repetition_datetime, time = sm2_next_repetition_date(dataset)
		return repetition_datetime, time


class UserWordRepetition(models.Model):
	word = models.ForeignKey(Word)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	time = models.IntegerField(null=True, default=None)
	repetition_date = models.DateField(null=True)


class UserStandalonePacket(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	words = ArrayField(
		models.IntegerField(),
		size=150, blank=True, null=True
	)

	def to_dict(self, user=None) -> dict:
		"""
		:param user: user object
		:type user: User
		:returns: A dictionary of packet which can be safely turned into json
		:rtype: dict
		"""
		data = dict()
		data['pk'] = 99999999
		data['name'] = 'Пользовательский пакет'
		data['lessonNumber'] = None
		data['demo'] = True
		if user and user.is_authenticated:
			data['activated'] = True
			data['added'] = True
		data['wordsCount'] = self.words.__len__()
		return data



class Example(models.Model):
	word = models.ForeignKey(Word)
	example = models.CharField(max_length=200)
	translation = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
