from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q

from le_francais_dictionary.consts import GENRE_CHOICES,\
    PARTOFSPEECH_CHOICES,\
    PARTOFSPEECH_NOUN, GENRE_MASCULINE, GENRE_FEMININE
from le_francais_dictionary.utils import sm2_response_quality, \
    sm2_next_repetition_date, ignore_whitespaces
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
        data['demo'] = self.demo
        if user and user.is_authenticated:
            data['activated'] = True if self.lesson.payed(user) else False
            if self.userpacket_set.filter(user=user).exists():
                userpacket = self.userpacket_set.filter(user=user).first()
                data['added'] = True
                data['wordsLearned'] = userpacket.words_learned
            else:
                data['added'] = False
                data['wordsLearned'] = None
        else:
            data['activated'] = None
            data['added'] = None
            data['wordsLearned'] = None
        data['wordsCount'] = self.words.all().count()
        return data

    def create_polly_task(self):
        for w in self.words.all():
            w.create_polly_task()

    @property
    def words_count(self):
        return self.words.all().count()

    def _fully_voiced(self):
        if self.words.filter(Q(polly__isnull=True) | Q(
                wordtranslation__polly__isnull=True)).exists():
            return False
        else:
            return True
    _fully_voiced.boolean = True
    fully_voiced = property(_fully_voiced)


class UserPacket(models.Model):
    packet = models.ForeignKey(Packet)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    @property
    def words_learned(self) -> int:  # TODO
        return self.packet.words.filter(
            userdata__user=self.user, userdata__grade=1).values(
            'word').distinct().__len__()


class Word(models.Model):
    cd_id = models.CharField(
        null=True,
        verbose_name='Color Dictionary ID',
        max_length=10)
    word = models.CharField(max_length=120, verbose_name='Word')
    polly = models.ForeignKey(PollyTask, null=True)
    genre = models.CharField(choices=GENRE_CHOICES, max_length=10, null=True,
                             verbose_name='Gender')
    part_of_speech = models.CharField(choices=PARTOFSPEECH_CHOICES,
                                      max_length=10, null=True,
                                      verbose_name='Part of Speech')
    plural = models.BooleanField(default=False, verbose_name='Plural')
    packet = models.ForeignKey(Packet, null=True, default=None)
    packets = models.ManyToManyField(Packet, related_name='words',
                                     null=True, default=None,
                                     through='WordPacket')

    @property
    def polly_url(self):
        return self.polly.url if self.polly else None

    def get_repetition_date(self, user):
        self.userwordrepetition_set.filter(user=user, word=self)

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
            'packets': [
                packet.pk for packet in self.packets.all()
            ],
            'userData': None,  # TODO userdata
        }

    def create_polly_task(self):
        text = ignore_whitespaces(self.word)
        if (self.part_of_speech == PARTOFSPEECH_NOUN and
                self.genre == GENRE_MASCULINE):
            voice_id = polly_const.VOICE_ID_MATHIEU
        elif (self.part_of_speech == PARTOFSPEECH_NOUN and
              self.genre == GENRE_FEMININE):
            voice_id = polly_const.VOICE_ID_CELINE
        else:
            voice_id = polly_const.VOICE_ID_LEA
        polly_task = PollyTask(
            text=text,
            text_type=polly_const.TEXT_TYPE_TEXT,
            language_code=polly_const.LANGUAGE_CODE_FR,
            output_format=polly_const.OUTPUT_FORMAT_MP3,
            sample_rate=polly_const.SAMPLE_RATE_22050,
            voice_id=voice_id,
        )
        polly_task.create_task('polly-dictionaries/words/', wait=False,
                               save=True)
        self.polly = polly_task
        self.save()
        for translation in self.wordtranslation_set.all():
            translation.create_polly_task()

    def __str__(self):
        return self.word


class WordPacket(models.Model):
    word = models.ForeignKey(Word)
    packet = models.ForeignKey(Packet)


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
        text = ignore_whitespaces(self.translation)
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

    def __str__(self):
        return self.translation


class UserWordData(models.Model):
    word = models.ForeignKey(Word, related_name='userdata')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    datetime = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField()
    mistakes = models.IntegerField()

    def response_quality(self):
        return sm2_response_quality(self.grade, self.mistakes)

    def get_repetition_datetime(self):
        dataset = UserWordData.objects.filter(word=self.word, user=self.user,
                                              datetime__lte=self.datetime)
        repetition_datetime, time = sm2_next_repetition_date(dataset)
        return repetition_datetime, time


class UserWordRepetition(models.Model):
    word = models.ForeignKey(Word)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    time = models.IntegerField()
    repetition_date = models.DateField(null=True)


class Example(models.Model):
    word = models.ForeignKey(Word)
    example = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
