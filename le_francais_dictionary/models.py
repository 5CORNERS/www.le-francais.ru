import re
from typing import List

from polly.const import LANGUAGE_CODE_FR, LANGUAGE_CODE_RU
from .tts import google_cloud_tts, shtooka_by_title_in_path, \
	FTP_FR_VERBS_PATH, FTP_RU_VERBS_PATH, \
	FTP_FR_WORDS_PATH, FTP_RU_WORDS_PATH, pytts_voice_string
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.http import urlquote
from regex import regex

from le_francais_dictionary.consts import GENRE_CHOICES, \
	PARTOFSPEECH_CHOICES, \
	PARTOFSPEECH_NOUN, GENRE_MASCULINE, GENRE_FEMININE, \
	GRAMMATICAL_NUMBER_CHOICES, PARTOFSPEECH_ADJECTIVE, TENSE_CHOICES, \
	TYPE_CHOICES, GENRE_EPICENE, GENRE_BOTH
from le_francais_dictionary.utils import format_text2speech, \
	create_or_update_repetition, \
	remove_parenthesis, clean_filename, escape_non_url_characters
from .sm2 import WordSM2
from polly import const as polly_const
from polly.models import PollyTask

from django.contrib.auth import get_user_model

User = get_user_model()

ADJECTIVE_GENRE_PARENTHESIS_PATTERN = '(\(.+?\))'

class Packet(models.Model):
	name = models.CharField(max_length=128)
	demo = models.BooleanField(default=False)
	lesson = models.ForeignKey('home.LessonPage',
	                           related_name='dictionary_packets', null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return f'{self.name}'

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
			else:
				data['activated'] = False
				data['added'] = False
			data['wordsLearned'] = self.words_learned(user)
			data['wordsChecked'] = self.words_checked(user)
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
		if self.lesson and self.lesson.payed(user):
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

	def words_checked(self, user) -> int:
		return len(self.word_set.filter(
			Q(userdata__user=user) | Q(userwordignore__user=user)
		).values('word').distinct())

	class Meta:
		ordering = ['lesson__lesson_number']


class UserPacket(models.Model):
	packet = models.ForeignKey(Packet, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	@property
	def words_learned(self) -> int:  # TODO
		return self.packet.word_set.filter(
			Q(userdata__user=self.user, userdata__grade=1)|Q(
				userwordignore__user=self.user
			)).values(
			'word').distinct().__len__()


class WordGroup(models.Model):
	def __str__(self):
		return f'{[w.word for w in self.word_set.all().order_by("order")]}'


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
	word_ssml = models.CharField(max_length=1000, null=True, default=None, blank=True)
	polly = models.ForeignKey(PollyTask, null=True, blank=True, on_delete=models.PROTECT)
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
	packet = models.ForeignKey(Packet, null=True, default=None, blank=True, on_delete=models.PROTECT)

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
		self._uni = None

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
		if self._uni is None:
			if self.group:
				try:
					self._uni = self.group.unifiedword_set.get(definition_num__exact=self.definition_num)
				except UnifiedWord.DoesNotExist:
					self._uni = EmptyUni()
			else:
				self._uni = EmptyUni()
		return self._uni

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
		"""
		:rtype: WordTranslation
		"""
		if self._first_translation is None:
			self._first_translation = self.wordtranslation_set.first()
		return self._first_translation

	@property
	def pos_html_class(self):
		if self.part_of_speech is not None:
			return f'pos-cc-enabled pos-{self.part_of_speech}'
		return ''

	@property
	def genre_html_class(self):
		if self.genre == GENRE_EPICENE:
			return 'genre-cc-enabled genre-epicene'
		elif self.genre == GENRE_BOTH:
			return 'genre-cc-enabled genre-both'
		elif self.genre == GENRE_MASCULINE:
			return 'genre-cc-enabled genre-masculine'
		elif self.genre == GENRE_FEMININE:
			return 'genre-cc-enabled genre-feminine'
		return ''

	@property
	def html_class(self):
		return f'{self.genre_html_class} {self.pos_html_class}'.strip()


	@property
	def table_html(self):
		if self.part_of_speech == PARTOFSPEECH_ADJECTIVE and self.genre == GENRE_BOTH:
			return re.sub(
				ADJECTIVE_GENRE_PARENTHESIS_PATTERN,
				r'<span class="genre-cc-enabled genre-feminine pos-cc-enabled pos-adj">\1</span>',
				self.word
			)
		return self.word

	def last_user_data(self, user):
		"""
		Returns:
			UserWordData:
		"""
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
		if user.is_authenticated and self.last_user_data(user):
			return float(round(self.last_user_data(user).mean_quality * 2) / 2)
		else:
			return None

	def mean_quality_filter_value(self, user):
		q = self.mean_quality(user)
		if user.is_authenticated and q is not None:
			return str(float(q)).replace('.', '@')
		else:
			return 'None'

	def get_repetition(self, user):
		if user.is_anonymous:
			return None
		if not user.pk in self._repetitions.keys():
			if self.group:
				repetition = UserWordRepetition.objects.filter(
					user=user,
					word__group_id=self.group_id,
					word__definition_num=self.definition_num,
				).order_by('-repetition_datetime').first()
			else:
				repetition = UserWordRepetition.objects.filter(
					user=user,
					word=self,
				).order_by('-repetition_datetime').first()
			if repetition:
				self._repetitions[user.pk] = repetition
			else:
				self._repetitions[user.pk] = None
		return self._repetitions[user.pk]

	def get_repetition_datetime(self, user):
		repetition = self.get_repetition(user)
		if repetition:
			return repetition.repetition_datetime
		else:
			return None

	def repetitions_count(self, user):
		repetition = self.get_repetition(user)
		if repetition:
			return repetition.time
		else:
			return None

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
		if user.is_anonymous:
			return False
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
			'unifiedWord': self.uni.word,
			'unifiedTranslation': self.uni.translation,
			'unifiedWordPollyUrl': self.uni.word_polly_url,
			'unifiedTranslationPollyUrl': self.uni.translation_polly_url,
		}
		if user and user.is_authenticated:
			repetition: UserWordRepetition = self.get_repetition(user)
			if repetition:
				repetition_time = repetition.time
				repetition_datetime = repetition.repetition_datetime
			else:
				repetition_time = None
				repetition_datetime = None
			data['userData'] = dict(
				nextRepetitionDate=repetition_datetime,
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

	def local_voice(self, save=False):
		if self.word_ssml:
			voice_string = self.word_ssml
		else:
			voice_string = f'<speak>{self.word}</speak>'
		voice_url = google_cloud_tts(
			voice_string,
			filename=f'{self.word}_synth',
			language=LANGUAGE_CODE_FR,
			genre=self.genre,
			file_id=self.cd_id,
			file_title=self.word,
			ftp_path=FTP_FR_WORDS_PATH,
		)
		self._polly_url = voice_url
		if save:
			self.save()

	def get_ssml(self):
		if self.word_ssml:
			if not '<speak>' in self.word_ssml:
				self.word_ssml = f'<speak>{self.word_ssml}</speak>'
			return self.word_ssml
		else:
			return f'<speak>{format_text2speech(self.word)}</speak>'

	def voice(self, save=True):
		filename = escape_non_url_characters(remove_parenthesis(self.word))
		ssml = self.get_ssml()
		if self.group:
			group_words = self.group.word_set.exclude(pk=self.pk).filter(polly__isnull=False, _polly_url__isnull=False)
			for group_word in group_words:
				group_word:Word
				if group_word.get_ssml() == ssml:
					if group_word.polly:
						self.polly = group_word.polly
					else:
						self._polly_url = group_word._polly_url
					if save:
						self.save()
					return self
		shtooka_url = None
		if not ('<speak>' in self.word_ssml
		        and 'gender=' in self.word_ssml):
			shtooka_url = shtooka_by_title_in_path(
				title=remove_parenthesis(self.word),
				ftp_path=FTP_FR_WORDS_PATH,
				language_code=LANGUAGE_CODE_FR,
				genre=self.genre, filename=filename)
		if shtooka_url:
			self._polly_url = shtooka_url
		else:
			self._polly_url = google_cloud_tts(
				s=ssml,
				ssml=True,
				filename=f'{escape_non_url_characters(remove_parenthesis(self.word))}_SYNTH',
				language=LANGUAGE_CODE_FR,
				genre=self.genre,
				file_id=self.cd_id,
				file_title=remove_parenthesis(self.word),
				ftp_path=FTP_FR_WORDS_PATH,
			)
		if save:
			self.save()
		return self


	def __str__(self):
		return f'Word:{self.cd_id} {self.word}'


class WordTranslation(models.Model):
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	translation = models.CharField(max_length=120, null=False, blank=False)
	translations_ssml = models.CharField(max_length=1000, null=True, default=None, blank=True)
	polly = models.ForeignKey(PollyTask, null=True, blank=True, on_delete=models.PROTECT)
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

	@property
	def html_class(self):
		return self.word.html_class

	@property
	def table_html(self):
		if self.word.part_of_speech == PARTOFSPEECH_ADJECTIVE and self.word.genre == GENRE_BOTH:
			return re.sub(
				ADJECTIVE_GENRE_PARENTHESIS_PATTERN,
				r'<span class="genre-cc-enabled genre-feminine pos-cc-enabled pos-adj">\1</span>',
				self.translation
			)
		return self.translation

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

	def local_voice(self, save=False):
		if self.translations_ssml:
			voice_string = self.translations_ssml
		else:
			voice_string = f'<speak>{self.translation}</speak>'
		voice_url = google_cloud_tts(
			voice_string,
			filename=f'{self.translation}_synth',
			language=LANGUAGE_CODE_RU,
			genre=self.genre,
			file_id=self.cd_id,
			file_title=self.translation,
			ftp_path=FTP_RU_WORDS_PATH,
		)
		self._polly_url = voice_url
		if save:
			self.save()

	def voice(self, save=True):
		filename = escape_non_url_characters(remove_parenthesis(self.translation))
		ssml = self.get_ssml()
		if self.word.group:
			group_words_ids = [w.cd_id for w in self.word.group.word_set.exclude(pk=self.word.pk)]
			group_translations = WordTranslation.objects.filter(word_id__in=group_words_ids).exclude(pk=self.pk)
			for group_translation in group_translations:
				group_translation:WordTranslation
				if group_translation.get_ssml() == ssml:
					voiced = True
					if group_translation.polly:
						self.polly = group_translation.polly
					elif group_translation._polly_url:
						self._polly_url = group_translation._polly_url
					else:
						voiced = False
					if save and voiced:
						self.save()
					if voiced:
						return self
		shtooka_url = None
		if not ('<speak>' in self.translations_ssml
		        and 'gender=' in self.translations_ssml):
			shtooka_url = shtooka_by_title_in_path(
				title=remove_parenthesis(self.translation),
				ftp_path=FTP_FR_WORDS_PATH,
				language_code=LANGUAGE_CODE_FR,
				filename=filename)
		if shtooka_url:
			self._polly_url = shtooka_url
		else:
			self._polly_url = google_cloud_tts(
				s=ssml,
				ssml=True,
				filename=f'{filename}_synth',
				language=LANGUAGE_CODE_RU,
				genre=self.genre,
				file_id=self.cd_id,
				file_title=remove_parenthesis(self.translation),
				ftp_path=FTP_RU_WORDS_PATH,
			)
		if save:
			self.save()
		return self

	def get_ssml(self):
		if self.translations_ssml:
			return self.translations_ssml
		else:
			return f'<speak>{format_text2speech(self.translation)}</speak>'


class UnifiedWord(models.Model):
	word = models.CharField(max_length=120)
	translation = models.CharField(max_length=120)
	definition_num = models.IntegerField(null=True, blank=True,
										 default=None)
	group = models.ForeignKey('WordGroup', on_delete=models.CASCADE)
	word_polly_url = models.URLField(max_length=1000, null=True,
									 default=None)
	translation_polly_url = models.URLField(max_length=1000, null=True,
											default=None)

	def __init__(self, *args, **kwargs):
		super(UnifiedWord, self).__init__(*args, **kwargs)
		self._original_translations = None
		self._original_word = None
		self._original_words = None

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

	@property
	def original_word(self) -> Word:
		if self._original_word is None:
			self._original_word = self.group.word_set.filter(
				definition_num=self.definition_num).first()
		return self._original_word

	@property
	def genre(self) -> str:
		return self.original_word.genre

	@property
	def part_of_speech(self) -> str:
		return self.original_word.part_of_speech

	@property
	def original_words(self) -> List[Word]:
		if self._original_words is None:
			self._original_words = list(self.group.word_set.filter(
				definition_num=self.definition_num
			))
		return self._original_words

	@property
	def original_translations(self) -> List[WordTranslation]:
		if self._original_translations is None:
			l = []
			for o_word in self.original_words:
				l.append(o_word.first_translation)
			self._original_translations = l
		return self._original_translations

	def voice(self, save=True):
		word_filename = clean_filename(self.word)
		if len(word_filename) > 50:
			word_filename = word_filename[:50]
		voiced_from_original = False
		for o_word in self.original_words:
			if o_word.polly_url and remove_parenthesis(
					o_word.word) == remove_parenthesis(self.word):
				self.word_polly_url = o_word.polly_url
				voiced_from_original = True
		if not voiced_from_original:
			shtooka_url = shtooka_by_title_in_path(
				title=remove_parenthesis(self.word),
				ftp_path=FTP_FR_WORDS_PATH,
				filename=clean_filename(self.word),
				genre=self.genre
			)
			if shtooka_url:
				self.word_polly_url = shtooka_url
			else:
				if self.part_of_speech == PARTOFSPEECH_NOUN and self.genre == GENRE_MASCULINE:
					self.word_polly_url = pytts_voice_string(
						s=remove_parenthesis(self.word),
						filename=clean_filename(self.word),
						tag_id=int(
							f'{self.group_id}{self.definition_num}'),
						tag_title=remove_parenthesis(self.word),
						genre=self.genre,
					)
				else:
					self.word_polly_url = google_cloud_tts(
						s=remove_parenthesis(self.word),
						filename=clean_filename(self.word),
						file_id=int(
							f'{self.group_id}{self.definition_num}'),
						file_title=remove_parenthesis(self.word),
						genre=self.genre,
						ftp_path=FTP_FR_WORDS_PATH,
						speaking_rate=0.8
					)

		translation_voiced_from_original = False
		translation_filename = clean_filename(self.translation)
		if len(translation_filename) > 50:
			translation_filename = translation_filename[:50]
		for o_translation in self.original_translations:
			if o_translation.polly_url and remove_parenthesis(
					o_translation.translation) == remove_parenthesis(
				self.translation):
				self.translation_polly_url = o_translation.polly_url
				translation_voiced_from_original = True
		if not translation_voiced_from_original:
			self.translation_polly_url = google_cloud_tts(
				s = remove_parenthesis(self.translation),
				filename=translation_filename,
				file_title=remove_parenthesis(self.translation),
				file_id=int(f'{self.group_id}{self.definition_num}'),
				genre=self.genre,
				language=LANGUAGE_CODE_RU,
				ftp_path=FTP_RU_WORDS_PATH,
				speaking_rate=1,
				ssml=False
			)
		if save:
			self.save(update_fields=['word_polly_url', 'translation_polly_url'])
		return self



class UserWordIgnore(models.Model):
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class UserWordData(models.Model):
	word = models.ForeignKey(Word, related_name='userdata', on_delete=models.PROTECT)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='flash_cards_data', on_delete=models.PROTECT)
	datetime = models.DateTimeField(auto_now_add=True)
	grade = models.IntegerField()
	mistakes = models.IntegerField()
	delay = models.IntegerField(null=True)
	custom_grade = models.IntegerField(null=True, default=None)
	timezone = models.CharField(null=True, max_length=32)

	def __init__(self, *args, **kwargs):
		super(UserWordData, self).__init__(*args, **kwargs)
		self._sm2_word_data = None
		self._user_word_dataset = None

	def __str__(self):
		return f'UserWordData: {self.user} -- {self.word} -- G/M/D: {self.grade}/' \
		       f'{self.mistakes}/{self.delay} -- Datetime: {self.datetime}'

	@property
	def sm2_word_data(self):
		if self._sm2_word_data is None:
			self._sm2_word_data = WordSM2(self.user_word_dataset)
		return self._sm2_word_data

	@property
	def user_word_dataset(self):
		if self._user_word_dataset is None:
			self._user_word_dataset = list(UserWordData.objects.select_related('word', 'user').filter(
				word=self.word, user=self.user,
				datetime__lte=self.datetime).order_by('datetime'))
		return self._user_word_dataset

	@property
	def e_factor(self):
		return self.sm2_word_data.e_factor

	@property
	def mean_quality(self):
		return self.sm2_word_data.mean_quality

	@property
	def quality(self):
		return self.sm2_word_data.last_quality

	def get_e_factor(self):
		return self.e_factor

	def get_repetition_datetime_and_time(self):
		return self.sm2_word_data.next_repetition, self.sm2_word_data.repetition_time

	def get_tz_aware_repetition_datetime_and_time(self) -> (datetime, int):
		repetition_datetime, time = self.get_repetition_datetime_and_time()
		if repetition_datetime is None:
			return None, None
		repetition_datetime = timezone.make_aware(
			timezone.make_naive(
				repetition_datetime, self.user.pytz_timezone
			).replace(
				hour=0, minute=0, second=0, microsecond=0),
			self.user.pytz_timezone)
		return repetition_datetime, time

	def update_or_create_repetition(self):
		repetition_datetime, time = self.get_tz_aware_repetition_datetime_and_time()
		if repetition_datetime:
			return create_or_update_repetition(
				self.user_id, self.word_id, repetition_datetime, time)
		return None


class UserWordRepetition(models.Model):
	word = models.ForeignKey(Word, on_delete=models.PROTECT)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	time = models.IntegerField(null=True, default=None)
	repetition_date = models.DateField(null=True) # obsolete
	repetition_datetime = models.DateTimeField(null=True)

	# FIXME: check for group words
	def update_repetition(self, save):
		last_data = self.word.last_user_data(user=self.user)
		datetime, self.time = last_data.get_repetition_datetime_and_time()
		datetime = timezone.make_aware(timezone.make_naive(datetime, self.user.pytz_timezone).replace(hour=0, minute=0, second=0, microsecond=0), self.user.pytz_timezone)
		self.repetition_datetime, self.repetition_date = datetime, datetime.date()
		if save:
			self.save()

	def __str__(self):
		return f'{self.user} -- {self.word} -- {self.repetition_datetime} -- {self.time}'


class UserDayRepetition(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	words_qty = models.IntegerField(null=True)
	repetitions = ArrayField(
		models.PositiveIntegerField(),
		blank=True, default=[]

	)
	date = models.DateField(null=True)
	datetime = models.DateTimeField(null=True)
	success = models.NullBooleanField(null=True)

	def __str__(self):
		return f'{self.datetime} -- {self.user}'


class UserStandalonePacket(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	filters = JSONField(default=None, null=True)
	words = ArrayField(
		models.IntegerField(),
		blank=True, null=True
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
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	example = models.CharField(max_length=200)
	translation = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)


class VerbPacket(models.Model):
	name = models.CharField(max_length=32)
	lesson = models.ForeignKey('home.LessonPage', on_delete=models.SET_NULL, null=True)

	def to_dict(self):
		result = []
		for verb_to_packet in VerbPacketRelation.objects.filter(packet=self).order_by('order'):
			# if verb_to_packet.verb.audio_url is None:
			# 	continue
			verb_dict = verb_to_packet.verb.to_dict()
			verb_dict['tense'] = verb_to_packet.tense
			verb_dict['forms'] = []
			for form in verb_to_packet.verb.verbform_set.filter(tense=verb_to_packet.tense).order_by('order'):
				verb_dict['forms'].append(form.to_dict())
			result.append(verb_dict)
		return result


class Verb(models.Model):
	verb = models.CharField(max_length=64)
	type = models.IntegerField(choices=TYPE_CHOICES, default=0)

	regular = models.BooleanField(default=True)
	translation = models.CharField(max_length=64, null=True)
	translation_text = models.CharField(max_length=64, null=True)
	packet = models.ForeignKey(VerbPacket, null=True, on_delete=models.SET_NULL)
	packets = models.ManyToManyField(VerbPacket, through='VerbPacketRelation' ,null=True, related_name='verbs')
	polly = models.ForeignKey(PollyTask, null=True, on_delete=models.SET_NULL, related_name='dictionary_verb_set')
	audio_url = models.URLField(null=True)
	translation_polly = models.ForeignKey(PollyTask, null=True,
	                                      on_delete=models.SET_NULL,
	                                      related_name='dictionary_verb_translation_set')
	translation_audio_url = models.URLField(null=True)

	def __init__(self, *args, **kwargs):
		super(Verb, self).__init__(*args, **kwargs)
		self._forms = None

	@property
	def forms(self):
		if self._forms is None:
			self._forms = list(self.verbform_set.all().order_by('order'))
		return self._forms

	def to_dict(self):
		polly_url = self.audio_url if self.audio_url else self.polly.url if self.polly else None
		if self.translation_audio_url:
			translation_polly_url = self.translation_audio_url
		elif self.translation_polly:
			translation_polly_url = self.translation_polly.url
		else:
			translation_polly_url = None
		# has_translation = True if self.translation else False
		return {
			"verb": self.verb,
			"pollyUrl": polly_url,
			"translation": self.translation,
			"trPollyUrl": translation_polly_url,
			"isTranslation": False,
			"isShownOnDrill": True,
			"packet": self.packet_id,
			"packets": [vpr.packet.pk for vpr in self.verbpacketrelation_set.all()],
			"type": self.type,
		}

	def to_voice(self, save=True, translation_language=LANGUAGE_CODE_RU, translation_genre=GENRE_MASCULINE):
		voice_string = self.verb.lower()
		voice_string = re.sub(r'\(.*\)', '', voice_string)
		voice_string = voice_string.strip()

		shtooka_url = shtooka_by_title_in_path(title=voice_string, ftp_path=FTP_FR_VERBS_PATH, verbs=True)
		if shtooka_url:
			self.audio_url = shtooka_url
			self.polly = None
		else:
			self.audio_url = google_cloud_tts(
				voice_string,
				filename=self.verb.replace(' ', '_').replace('\'', '_').replace('\\', '_'),
				language=LANGUAGE_CODE_FR,
				genre=GENRE_MASCULINE,
				file_id=str(self.pk),
				file_title=self.verb,
				ftp_path=FTP_FR_VERBS_PATH,
				speaking_rate=1,
				verbs=True
			)

		translation_shtooka_url = shtooka_by_title_in_path(
			title=self.translation_text or self.translation,
			ftp_path=FTP_RU_VERBS_PATH,
			language_code=translation_language,
			verbs=True
		)

		if not translation_shtooka_url:
			self.translation_audio_url = google_cloud_tts(
				self.translation_text or self.translation,
				filename=self.translation.replace(' ', '_'),
				language=translation_language,
				genre=translation_genre,
				file_id=str(self.pk),
				file_title=self.translation,
				ftp_path=FTP_RU_VERBS_PATH if translation_language == LANGUAGE_CODE_RU else FTP_FR_VERBS_PATH,
				speaking_rate=1,
				verbs=True,
			)
		else:
			self.translation_audio_url = translation_shtooka_url

		if save:
			self.save()
		return self


class VerbPacketRelation(models.Model):
	verb = models.ForeignKey(Verb, on_delete=models.CASCADE)
	packet = models.ForeignKey(VerbPacket, on_delete=models.CASCADE)
	order = models.PositiveIntegerField(default=1)
	tense = models.IntegerField(choices=TENSE_CHOICES, default=0)


class VerbForm(models.Model):
	tense = models.IntegerField(choices=TENSE_CHOICES, null=True, default=None)
	verb = models.ForeignKey(Verb, on_delete=models.CASCADE, null=True)
	order = models.PositiveSmallIntegerField(null=True)
	form = models.CharField(max_length=64, null=True)
	is_shown = models.BooleanField(default=1)
	form_to_show = models.CharField(max_length=64, null=True)
	translation = models.CharField(max_length=64, null=True)
	translation_text = models.CharField(max_length=64, null=True)
	polly = models.ForeignKey(PollyTask, null=True, on_delete=models.SET_NULL,
	                          related_name='dictionary_verb_form_set')
	audio_url = models.URLField(null=True)
	translation_polly = models.ForeignKey(PollyTask, null=True,
	                                      on_delete=models.SET_NULL,
	                                      related_name='dictionary_verb_form_translation_set')
	translation_audio_url = models.URLField(null=True)

	def to_dict(self):
		polly_url = self.audio_url if self.audio_url else self.polly.url if self.polly else None
		if self.translation_audio_url:
			translation_polly_url = self.translation_audio_url
		elif self.translation_polly:
			translation_polly_url = self.translation_polly.url
		else:
			translation_polly_url = None
		return {
			"form": self.form,
			"isShownOnDrill": self.is_shown,
			"formToShowOnDrill": self.form_to_show,
			"pollyUrl": polly_url,
			"translation": self.translation,
			"trPollyUrl": translation_polly_url,
			"type": self.verb.type,
			"tense": self.tense,
		}

	def to_voice(self, save=True, translation_language=LANGUAGE_CODE_RU, translation_genre=GENRE_MASCULINE):
		voice_string = self.form.lower()
		voice_string = re.sub(r'\(.*\)', '', voice_string)
		voice_string = voice_string.strip()

		shtooka_url = shtooka_by_title_in_path(
			title=voice_string,
			ftp_path=FTP_FR_VERBS_PATH,
			verbs=True
		)

		if not shtooka_url:
			if self.verb.verbform_set.filter(is_shown=True).order_by('order').last() == self:
				voice_string += '.'
			else:
				voice_string += ','
			self.audio_url = google_cloud_tts(
				voice_string,
				filename=self.form.replace(' ', '_').replace('\'', '_').replace('\\', '_'),
				language=LANGUAGE_CODE_FR,
				genre=GENRE_MASCULINE,
				file_id=str(self.pk),
				file_title=self.form,
				ftp_path=FTP_FR_VERBS_PATH,
				speaking_rate=1,
				verbs=True
			)
		else:
			self.audio_url = shtooka_url

		translation_shtooka_url = shtooka_by_title_in_path(
			title=self.translation_text or self.translation,
			ftp_path=FTP_RU_VERBS_PATH,
			language_code=translation_language,
			verbs=True
		)

		if not translation_shtooka_url:
			self.translation_audio_url = google_cloud_tts(
				self.translation_text or self.translation,
				filename=self.translation.replace(' ', '_'),
				language=translation_language,
				genre=translation_genre,
				file_id=str(self.pk),
				file_title=self.translation,
				ftp_path=FTP_RU_VERBS_PATH if translation_language == LANGUAGE_CODE_RU else FTP_FR_VERBS_PATH,
				speaking_rate=1,
				verbs=True
			)
		else:
			self.translation_audio_url=translation_shtooka_url

		if save:
			self.save(update_fields=['audio_url', 'translation_audio_url', 'polly'])
		return self


	class Meta:
		ordering = ['order']


def get_repetition_words_query(user, filter_excluded=True):
	q = Word.objects.filter(
		userwordrepetition__repetition_datetime__lte=timezone.now(),
		userwordrepetition__user=user,
		userwordrepetition__time__lt=5
	).distinct()
	if filter_excluded:
		q = q.exclude(userwordignore__user=user)
	return q


def prefetch_words_data(words, user):
	translations = list(
	WordTranslation.objects.filter(word__in=words))
	for word in words:
		word_translations = [wt for wt in translations if
		                     wt.word_id == word.pk]
		if word_translations:
			word._first_translation = word_translations[0]
		else:
			word._first_translation = None
	if user.is_authenticated:
		groups = list(WordGroup.objects.filter(word__in=words))
		groups_words = list(Word.objects.filter(group__in=groups))
		groups_words_repetitions = list(
			UserWordRepetition.objects.prefetch_related('word__group').filter(
				user=user, word__in=groups_words).order_by('-time'))
		groups_user_data = list(
			UserWordData.objects.prefetch_related('word__group').filter(
				user=user, word__in=groups_words).order_by('-datetime')
		)
		ignored = list(
			UserWordIgnore.objects.filter(user=user, word__in=words))
		user_data = list(
			UserWordData.objects.select_related('word').filter(user=user, word__in=words).order_by(
				'-datetime'))
		user_repetitions = list(
			UserWordRepetition.objects.filter(user=user, word__in=words))
		word: Word
		for word in words:
			group = next(
				(group for group in groups if group.pk == word.group_id),
				None)
			if group:
				group_repetition = next(
					(rep for rep in groups_words_repetitions if
					 rep.word.group_id == group.pk), None)
				if group_repetition:
					word._repetitions[user.pk] = \
						group_repetition
				else:
					word._repetitions[user.pk] = None
				# don't really sure about this
				group_user_dataset = [ud for ud in groups_user_data if ud.word.group_id == group.pk]
				if group_user_dataset:
					last_word_user_data = group_user_dataset[0]
					last_word_user_data._user_word_dataset = group_user_dataset
					word._last_user_data[user.pk] = last_word_user_data
				else:
					word._last_user_data[user.pk] = None
			else:
				user_word_repetitions = [uwr for uwr in user_repetitions if
				                         uwr.word_id == word.pk]
				if user_word_repetitions:
					word._repetitions[user.pk] = \
						user_word_repetitions[0]
				else:
					word._repetitions[user.pk] = None
				word_user_data = [ud for ud in user_data if
				                  ud.word_id == word.pk]
				if word_user_data:
					last_word_user_data = word_user_data[0]
					last_word_user_data._user_word_dataset = word_user_data
					word._last_user_data[user.pk] = last_word_user_data
				else:
					word._last_user_data[user.pk] = None

			if word.pk in [i.word_id for i in ignored]:
				word._is_marked[user.pk] = True
			else:
				word._is_marked[user.pk] = False
	return words


class DictionaryError(models.Model):
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	message = models.TextField(null=True)
	datetime_creation = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.message[:20] + '...'
