from django.conf import settings
from django.db import models

from polly import const as polly_const
from polly.models import PollyTask


class Word(models.Model):
	GENRE_FEMININE = 'f'
	GENRE_MASCULINE = 'm'
	GENRE_CHOICES = [
		(GENRE_FEMININE, 'Feminine'),
		(GENRE_MASCULINE, 'Masculine')
	]
	word = models.CharField(max_length=50)
	polly = models.ForeignKey(PollyTask, null=True)
	cd_id = models.IntegerField(null=True)
	genre = models.CharField(choices=GENRE_CHOICES, max_length=1, null=True)
	lessons = models.ManyToManyField('home.LessonPage', related_name='dictionary_words', null=True)

	@property
	def polly_url(self):
		if self.polly is None:
			return None
		else:
			return self.polly.url

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
	translation = models.CharField(max_length=50)
	polly = models.ForeignKey(PollyTask, null=True)

	@property
	def polly_url(self):
		if self.polly is None:
			return None
		else:
			return self.polly.url

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


class Example(models.Model):
	word = models.ForeignKey(Word)
	example = models.CharField(max_length=200)
	translation = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
