from datetime import datetime

from django.conf import settings
from django.db import models
from django_bulk_update.manager import BulkUpdateManager

from le_francais_dictionary.consts import GENRE_CHOICES, PARTOFSPEECH_CHOICES
from polly import const as polly_const
from polly.models import PollyTask


class Packet(models.Model):
	name = models.CharField(max_length=128)
	lesson = models.ForeignKey('home.LessonPage', related_name='dictionary_packets', null=True)

	def __str__(self):
		return '{self.name}'.format(self=self)


class Word(models.Model):
	cd_id = models.CharField(null=True, verbose_name='Color Dictionary ID',
	                         max_length=10)
	word = models.CharField(max_length=120, verbose_name='Word')
	polly = models.ForeignKey(PollyTask, null=True)
	genre = models.CharField(choices=GENRE_CHOICES, max_length=4, null=True, verbose_name='Gender')
	part_of_speech = models.CharField(choices=PARTOFSPEECH_CHOICES, max_length=6, null=True, verbose_name='Part of Speech')
	plural = models.BooleanField(default=False, verbose_name='Plural')
	packet = models.ForeignKey(Packet, null=True)

	@property
	def polly_url(self):
		return self.polly.url if self.polly else None

	def to_dict(self, with_user=False, user=None):
		return {
			'pk': self.pk,
			'word': self.word,
			'pollyUrl': self.polly_url,
			'gender': self.genre,
			'partOfSpeech': self.part_of_speech,
			'plural': self.plural,
			'translations': [
				tr.to_dict() for tr in self.wordtranslation_set.all()
			],
			'packet':self.packet.pk,
			'userData': self.userword_set.get(user=user).to_dict() if with_user else None,
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


class UserWord(models.Model):

	word = models.ForeignKey(Word, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
	                         on_delete=models.CASCADE)
	update_datetime = models.DateTimeField(default=None)
	stars = models.IntegerField(default=None)

	def to_dict(self):
		return {
			'datetime': self.update_datetime.isoformat(),
			'stars': self.stars,
		}

	@property
	def difficulty(self):
		...
		return

	@property
	def next_datetime(self):
		...
		return


class UserWordData(models.Model):
	user_word = models.ForeignKey(UserWord)
	date = models.DateField(auto_now_add=True)
	grade = models.IntegerField()
	mistakes = models.IntegerField()


class Example(models.Model):
	word = models.ForeignKey(Word)
	example = models.CharField(max_length=200)
	translation = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
