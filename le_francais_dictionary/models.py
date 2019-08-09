from django.conf import settings
from django.db import models

from polly import const as polly_const
from polly.models import PollyTask


class Word(models.Model):
	GENRE_FEMININE = 'f'
	GENRE_MASCULINE = 'm'
	GENRE_EPICENE = 'm/f'
	GENRE_BOTH = 'm(f)'
	GENRE_CHOICES = [
		(GENRE_FEMININE, 'Feminine'),
		(GENRE_MASCULINE, 'Masculine'),
		(GENRE_EPICENE, 'Epicene'),
		(GENRE_BOTH, 'Both in one')
	]
	PARTOFSPEECH_NOUN = 'nom'
	PARTOFSPEECH_PRONOUN = 'pron'
	PARTOFSPEECH_ADJECTIVE = 'adj'
	PARTOFSPEECH_ADVERB = 'adv'
	PARTOFSPEECH_CONJUNCTION = 'conj'
	PARTOFSPEECH_VERB = 'verb'
	PARTOFSPEECH_PREPOSITION = 'prep'
	PARTOFSPEECH_INTERJECTION = 'interj'
	PARTOFSPEECH_LOCUTION = 'loc'
	PARTOFSPEECH_PHRASE = 'phrase'
	PARTOFSPEECH_CHOICES = [
		(PARTOFSPEECH_NOUN, 'Noun'),
		(PARTOFSPEECH_PRONOUN, 'Pronoun'),
		(PARTOFSPEECH_ADJECTIVE, 'Adjective'),
		(PARTOFSPEECH_ADVERB, 'Adverb'),
		(PARTOFSPEECH_CONJUNCTION, 'Conjunction'),
		(PARTOFSPEECH_VERB, 'Verb'),
		(PARTOFSPEECH_PREPOSITION, 'Preposition'),
		(PARTOFSPEECH_INTERJECTION, 'Interjection'),
		(PARTOFSPEECH_LOCUTION, 'Locution'),
		(PARTOFSPEECH_PHRASE, 'Phrase'),
	]
	cd_id = models.CharField(null=True, verbose_name='Color Dictionary ID',
	                         max_length=10)
	word = models.CharField(max_length=120, verbose_name='Word')
	polly = models.ForeignKey(PollyTask, null=True)
	genre = models.CharField(choices=GENRE_CHOICES, max_length=4, null=True, verbose_name='Gender')
	part_of_speech = models.CharField(choices=PARTOFSPEECH_CHOICES, max_length=6, null=True, verbose_name='Part of Speech')
	plural = models.BooleanField(default=False, verbose_name='Plural')
	lessons = models.ManyToManyField('home.LessonPage',
	                                 related_name='dictionary_words',
	                                 null=True)

	@property
	def polly_url(self):
		return self.polly.url if self.polly else None

	def to_dict(self):
		return {
			'word': self.word,
			'translations': [
				tr.to_dict() for tr in self.wordtranslation_set.all()
			],
			'lessons': [
				lesson_page.lesson_number for lesson_page in self.lessons.all()
			],
			'gender': self.genre,
			'partOfSpeech': self.part_of_speech,
			'plural': self.plural,
			'pollyUrl': self.polly_url,
			'pk': self.pk,
		}

	def create_polly_task(self):
		if self.polly is None:
			polly_task = PollyTask(
				text=self.word,
				text_type=polly_const.TEXT_TYPE_TEXT,
				language_code=polly_const.LANGUAGE_CODE_FR,
				output_format=polly_const.OUTPUT_FORMAT_MP3,
				sample_rate=polly_const.SAMPLE_RATE_22050,
				voice_id=polly_const.VOICE_ID_LEA,
			)
			polly_task.create_task('polly-dictionaries/words/', wait=True,
			                       save=True)
			self.polly = polly_task
			self.save()

	def __str__(self):
		return self.word


class WordTranslation(models.Model):
	word = models.ForeignKey(Word)
	translation = models.CharField(max_length=120)
	polly = models.ForeignKey(PollyTask, null=True)

	@property
	def polly_url(self):
		if self.polly is None:
			return None
		else:
			return self.polly.url

	def to_dict(self):
		return {
			'translation': self.translation,
			'pollyUrl': self.polly_url,
		}

	def create_polly_task(self):
		if self.polly is None:
			polly_task = PollyTask(
				text=self.translation,
				text_type=polly_const.TEXT_TYPE_TEXT,
				language_code=polly_const.LANGUAGE_CODE_FR,
				output_format=polly_const.OUTPUT_FORMAT_MP3,
				sample_rate=polly_const.SAMPLE_RATE_22050,
				voice_id=polly_const.VOICE_ID_LEA,
			)
			polly_task.create_task('polly-dictionaries/translations/',
			                       wait=True,
			                       save=True)
			self.polly = polly_task
			self.save()

	def __str__(self):
		return self.translation


class WordUser(models.Model):
	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
	                         on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)

	def to_dict(self):
		return {
			'word': self.word.pk,
			'datetime': self.datetime, # TODO: serialize datetime to json
		}


class Example(models.Model):
	word = models.ForeignKey(Word)
	example = models.CharField(max_length=200)
	translation = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
