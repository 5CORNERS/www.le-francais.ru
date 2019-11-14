import datetime
import json
import random

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from le_francais_dictionary.views import update_words
from wagtail.core.models import Page, Site
from home.models import LessonPage, UserLesson
from .models import Word, WordTranslation, Packet, UserPacket, UserWordData, \
    UserWordRepetition
from . import views
from . import consts

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


def tick_10_seconds(frozen_time):
    frozen_time.tick(delta=datetime.timedelta(seconds=10))


class WordUserTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='user1',
                                             email='user1@email.com',
                                             password='password')
        root_page = Page.get_root_nodes()[0]
        root_page.add_child(
            instance=LessonPage(
                title='lesson1',
                slug='lesson1',
                lesson_number=1
            )
        )
        root_page.add_child(
            instance=LessonPage(
                title='lesson2',
                slug='lesson2',
                lesson_number=2
            )
        )
        self.packet1 = Packet.objects.create(
            name='packet1',
            lesson=LessonPage.objects.get(lesson_number=1),
            demo=True
        )
        self.packet2 = Packet.objects.create(
            name='packet2',
            lesson=LessonPage.objects.get(lesson_number=2)
            )
        self.word1 = Word.objects.create(word='word1', packet=self.packet1, cd_id=1)
        self.word2 = Word.objects.create(word='word2', packet=self.packet1, cd_id=2)
        self.word3 = Word.objects.create(word='word3', packet=self.packet2, cd_id=3)
        self.word4 = Word.objects.create(word='word4', packet=self.packet2, cd_id=4)

    def test_add_demo_packet(self):
        data = dict(
            packets=[self.packet1.pk]
        )
        expecting_response = {
            'added': [self.packet1.pk],
            'alreadyExisted': [],
            'errors': []
        }
        request = self.factory.post(reverse('dictionary:add_packets'),
                                    data=json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        response = views.add_packets(request)
        self.assertDictEqual(
            json.loads(response.content),
            expecting_response
        )
        expecting_response = {
            'added': [],
            'alreadyExisted': [self.packet1.pk],
            'errors': []
        }
        response = views.add_packets(request)
        self.assertDictEqual(
            json.loads(response.content),
            expecting_response
        )

    def test_add_normal_packet(self):
        data = dict(
            packets=[self.packet2.pk]
        )
        expecting_response = {
            'added': [],
            'alreadyExisted': [],
            'errors': [
                {
                    'pk': self.packet2.pk,
                    'message': consts.LESSON_IS_NOT_ACTIVATED_MESSAGE,
                    'code': consts.LESSON_IS_NOT_ACTIVATED_CODE,
                }
            ]
        }
        request = self.factory.post(reverse('dictionary:add_packets'),
                                    data=json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        response = views.add_packets(request)
        self.assertDictEqual(
            json.loads(response.content),
            expecting_response
        )
        # activating lesson2
        UserLesson.objects.create(
            user=self.user,
            lesson=LessonPage.objects.get(slug='lesson2')
        )
        expecting_response = {
            'added': [self.packet2.pk],
            'alreadyExisted': [],
            'errors': []
        }
        response = views.add_packets(request)
        self.assertDictEqual(
            json.loads(response.content),
            expecting_response
        )

    def test_add_packets_user_is_not_authenticated(self):
        data = dict(
            packets=[self.packet1.pk, self.packet2.pk]
        )
        request = self.factory.post(reverse('dictionary:add_packets'),
                                    data=json.dumps(data),
                                    content_type='application/json')
        request.user = AnonymousUser()
        response = views.add_packets(request)
        self.assertDictEqual(
            json.loads(response.content),
            dict(
                added=[],
                already_exist=[],
                errors=[
                    {"packet": self.packet1.pk,
                     "message": consts.USER_IS_NOT_AUTHENTICATED_MESSAGE},
                    {"packet": self.packet2.pk,
                     "message": consts.USER_IS_NOT_AUTHENTICATED_MESSAGE}
                ],
            ))

    def test_add_packets_packet_do_not_exist_lesson_is_not_activated(self):
        data = dict(
            packets=[9999, self.packet2.pk]
        )
        request = self.factory.post(reverse('dictionary:add_packets'),
                                    data=json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        response = views.add_packets(request)
        self.assertDictEqual(
            json.loads(response.content),
            dict(
                added=[],
                already_exist=[],
                errors=[
                    {"packet": 9999,
                     "message": consts.PACKET_DOES_NOT_EXIST_MESSAGE},
                    {"packet": self.packet2.pk,
                     "message": consts.LESSON_IS_NOT_ACTIVATED_MESSAGE}
                ],
            ))

    def test_get_progress(self):
        request = self.factory.get(reverse('dictionary:get_progress'))
        request.user = self.user
        response = views.get_progress(request)
        expect = {'packets': [packet.to_dict(self.user) for packet in Packet.objects.all().order_by('lesson__lesson_number')]}
        self.assertDictEqual(
            json.loads(response.content),
            expect,
        )

    def test_update_words(self):
        initial_datetime = datetime.datetime(1, 1, 1, 12, 0, 0)

        update_words_url = reverse('dictionary:update_words')
        data = dict(
            packets=[self.packet2.pk]
        )
        add_packet_request = self.factory.post(
            reverse('dictionary:add_packets'), data=json.dumps(data),
            content_type='application/json')
        add_packet_request.user = self.user
        views.add_packets(add_packet_request)

        grades_choices = [0] * 5 + [1] * 5
        mistakes_choices = [0] * 5 + [1] * 4 + [2] * 3 + [3] * 2
        with freeze_time(initial_datetime) as frozen_datetime:
            for step in range(5):
                for word in self.packet2.word_set.all():
                    frozen_datetime.tick(delta=datetime.timedelta(seconds=10))
                    remembering = True
                    while remembering:
                        frozen_datetime.tick(
                            delta=datetime.timedelta(seconds=10))
                        grade = random.choice(grades_choices)
                        mistakes = random.choice(mistakes_choices)
                        data = {
                            'words': [
                                {
                                    'pk': word.pk,
                                    'grade': grade,
                                    'mistakes': mistakes,
                                }
                            ]
                        }
                        request = self.factory.post(
                            update_words_url,
                            json.dumps(data),
                            'application/json'
                        )
                        request.user = self.user
                        response = views.update_words(request)
                        if grade:
                            remembering = False
                passing = True
                while passing:
                    if UserWordRepetition.objects.filter(
                            repetition_date__gt=timezone.now()):
                        frozen_datetime.tick(delta=datetime.timedelta(days=1))
                    else:
                        passing = False
