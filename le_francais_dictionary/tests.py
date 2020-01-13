import datetime
import json
import random
import string

from django.core.management import call_command
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
SEED = 30

def random_string(string_length=10) -> str:
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    # random.seed(SEED)
    return ''.join(random.choice(letters) for i in range(string_length))

def tick_10_seconds(frozen_time):
    frozen_time.tick(delta=datetime.timedelta(seconds=10))


def create_test_word_packet(lesson_number, quantity, starting_pk):
    # random.seed(SEED)
    lesson_title = random_string(10).upper()
    root_page = Page.get_root_nodes()[0]
    root_page.add_child(
        instance=LessonPage(
            title=lesson_title,
            slug=lesson_title,
            lesson_number=lesson_number
        )
    )
    packet = Packet.objects.create(
        name=lesson_title,
        lesson=LessonPage.objects.get(slug=lesson_title)
    )
    for i in range(quantity):
        # random.seed(SEED)
        Word.objects.create(word=random_string(5), packet=packet, cd_id=starting_pk)
        starting_pk += 1
    return packet, starting_pk

def random_answer(quality=None):
    # random.seed(SEED)
    grade = random.choice([1] * 8 + [0] * 2)
    # random.seed(SEED)
    mistakes = random.choice([0]*70 + [1]*20 + [2]*10)
    # random.seed(SEED)
    delay = random.random() * 10000
    return grade, mistakes, delay

def return_words_object_from_json(json_data):
    return [Word.objects.get(cd_id=word_data['pk']) for word_data in
            json_data['words']]

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
        self.good = [self.word1, self.word3]

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

        UserLesson.objects.create(
            user=self.user,
            lesson=LessonPage.objects.get(slug='lesson2')
        )

        update_words_url = reverse('dictionary:update_words')
        data = dict(
            packets=[self.packet2.pk]
        )

        s_good = []
        s_bad = []

        good_grades_choices = [1]
        bad_grades_choices = [0] * 5 + [1] * 5
        good_mistakes_choices = [0]
        bad_mistakes_choices = [0] * 5 + [1] * 10 + [2] * 5 + [3] * 2
        learning = True
        words = list(self.packet2.word_set.all())
        with freeze_time(initial_datetime) as frozen_datetime:
            while learning:
                for i, word in reversed(list(enumerate(words))):
                    frozen_datetime.tick(delta=datetime.timedelta(seconds=10))
                    remembering = True
                    while remembering:
                        frozen_datetime.tick(
                            delta=datetime.timedelta(seconds=10))
                        if word in self.good:
                            # random.seed(SEED)
                            grade = random.choice(good_grades_choices)
                            # random.seed(SEED)
                            mistakes = random.choice(good_mistakes_choices)
                        else:
                            # random.seed(SEED)
                            grade = random.choice(bad_grades_choices)
                            # random.seed(SEED)
                            mistakes = random.choice(bad_mistakes_choices)
                        mistakes_ratio = word.mistake_ratio(mistakes)
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
                        response_data = (json.loads(response.content))['words'][0]
                        e_factor = response_data['e_factor']
                        quality = response_data['quality']
                        mean_quality = response_data['mean_quality']
                        times = response_data['repetitionTime']
                        today = datetime.datetime.today().strftime('%Y/%m/%d')
                        if word in self.good:
                            s_good.append([today,times,grade,mistakes_ratio,e_factor,quality, mean_quality])
                        else:
                            s_bad.append([today,times,grade,mistakes_ratio,e_factor,quality, mean_quality])
                        if response_data['repetitionTime'] == 5:
                            words.pop(i)
                        if grade:
                            remembering = False
                passing = True
                if not words:
                    learning = False
                while passing:
                    if UserWordRepetition.objects.filter(
                            repetition_date__gt=timezone.now()):
                        frozen_datetime.tick(delta=datetime.timedelta(days=1))
                    else:
                        passing = False
        col_width = max(
            len(str(word)) for row in s_good for word in row) + 2  # padding
        for row in s_good:
            print("".join(str(word).ljust(col_width) for word in row))

        col_width = max(
            len(str(word)) for row in s_bad for word in row) + 2  # padding
        for row in s_bad:
            print("".join(str(word).ljust(col_width) for word in row))


class FlashCardsTestCase(TestCase):
    def setUp(self):
        from .utils import FIRST_REPETITION_DELTA, SECOND_REPETITION_DELTA
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpassword',
                                             timezone='Europe/Moscow')
        self.packet, last_pk = create_test_word_packet(1, 20, 0)

    def test1(self):
        UserLesson.objects.create(user=self.user, lesson=self.packet.lesson)
        get_words_request = self.factory.get(path=reverse('dictionary:get_words', args=[self.packet.pk]))
        get_words_request.user=self.user
        get_words_response = views.get_words(get_words_request, self.packet.pk)
        get_words_data = json.loads(get_words_response.content)
        if not get_words_data['words']:
            self.fail('get_words method returning empty list or None')
        words = []
        initial_datetime = datetime.datetime(1, 1, 1, 12, 0, 0)
        for word_data in get_words_data['words']:
            word = Word.objects.get(cd_id=word_data['pk'])
            words.append(word)
        with freeze_time(initial_datetime) as frozen_datetime:
            def repeat_words(repeating_words):
                repeating = 'in progress'
                repeating_words = list(repeating_words)
                print("---------------")
                print("Repeating words")
                print('---------------')
                while repeating != 'done':
                    for i, repeating_word in reversed(list(enumerate(repeating_words))):
                        grade, mistakes, delay = random_answer()
                        post_update_words_request = self.factory.post(
                            path=reverse('dictionary:update_words'),
                            data=json.dumps(dict(
                                words=[
                                    {
                                        "pk": repeating_word.pk,
                                        "grade": grade,
                                        "mistakes": mistakes,
                                        "delay": delay,
                                    }
                                ]
                            )),
                            content_type='application/json'
                        )
                        frozen_datetime.tick(
                            datetime.timedelta(milliseconds=delay))
                        post_update_words_request.user = self.user
                        update_response = views.update_words(
                            post_update_words_request)
                        update_data = json.loads(update_response.content)
                        repetition_time = update_data['words'][0][
                            'repetitionTime']
                        print(f'Repeated word: {repeating_word} -- '
                              f'{grade} -- '
                              f'{mistakes} -- '
                              f'{delay} -- '
                              f'{repetition_time}')
                        if grade:
                            repeating_words.pop(i)
                            self.assertTrue(repetition_time < 6,
                                            'Repetition time can\'t be more than 5')
                            if not repeating_words:
                                repeating = 'done'
                        else:
                            self.assertIsNone(repetition_time)
            repeat_words(words)

            from notifications import views as notifications_views
            from notifications.models import Notification
            def get_notifications():
                get_new_notifications_request = self.factory.get(
                    reverse('notifications:get_new'))
                get_new_notifications_request.user=self.user
                new_notifications_response = notifications_views.get_new_notifications(get_new_notifications_request)
                new_notifications_data = json.loads(new_notifications_response.content)
                notifications = []
                if new_notifications_data['notification_list']:
                    for notification_data in new_notifications_data['notification_list']:
                        notification = Notification.objects.get(pk=notification_data['pk'])
                        notification.active = False
                        notification.save()
                        notifications.append(notification)
                    return notifications
                else:
                    return None
            def get_repetition_words():
                repetition_words_request = self.factory.get(
                    path=reverse('dictionary:get_repetitions'))
                repetition_words_request.user = self.user
                repetition_words_response = views.get_repetition_words(
                    repetition_words_request)
                repetition_words_data = json.loads(
                    repetition_words_response.content)
                words_for_repetition = return_words_object_from_json(repetition_words_data)
                return words_for_repetition

            while UserWordRepetition.objects.filter(time__lte=5).exists():
                notifications = []
                print('++++++++++++++++++++++++')
                print('Waiting for notification')
                print('++++++++++++++++++++++++')
                while not notifications:
                    notifications = get_notifications()
                    frozen_datetime.tick(datetime.timedelta(hours=1))
                    call_command('create_dictionary_notifications')
                    self.failIf(isinstance(notifications, list) and len(notifications) > 1, 'Created more than one notifications')
                print(timezone.now())
                repetition_words = get_repetition_words()
                self.assertTrue(len(repetition_words) > 0, 'No repetitions while notification has come')
                self.assertEqual(len(notifications[0].content_object.repetitions),
                                 len(repetition_words),
                                 msg = f'Wrong words quantity\n'
                                       f'{[UserWordRepetition.objects.get(pk=x).word for x in notifications[0].content_object.repetitions]}\n'
                                       f'{repetition_words}')
                repeat_words(repetition_words)
