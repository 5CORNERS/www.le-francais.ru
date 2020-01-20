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
    UserWordRepetition, WordGroup, UserWordIgnore
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


class FlashCardsTestCase(TestCase):
    def setUp(self):
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


class FlashCardsGroupWordsTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpassword',
                                             timezone='Europe/Moscow')
        self.packet1, next_pk = create_test_word_packet(1, 1, 0)
        self.packet2, next_pk = create_test_word_packet(2, 1, next_pk)
        self.word_group = WordGroup.objects.create()
        word1 = self.packet1.word_set.first()
        word1.group = self.word_group
        word1.save()
        self.word1 = word1
        word2 = self.packet2.word_set.first()
        word2.group = self.word_group
        word2.save()
        self.word2 = word2
        UserLesson.objects.create(user=self.user, lesson=self.packet1.lesson)
        UserLesson.objects.create(user=self.user, lesson=self.packet2.lesson)

    def test1(self):
        with freeze_time(datetime.datetime(1,1,1,0,0,0)) as freeze_datetime:
            update_words_request_word1 = self.factory.post(
                path=reverse('dictionary:update_words'),
                data=json.dumps({
                    "words":[
                        {
                            "pk":self.word1.pk,
                            "grade":1,
                            "mistakes": 0,
                            "delay": 3000
                        }
                    ]
                }),
                content_type='application/json'
            )
            update_words_request_word1.user = self.user
            word1_response = views.update_words(update_words_request_word1)
            freeze_datetime.tick(datetime.timedelta(seconds=10))
            update_words_request_word2 = self.factory.post(
                path=reverse('dictionary:update_words'),
                data=json.dumps({
                    "words": [
                        {
                            "pk": self.word2.pk,
                            "grade": 1,
                            "mistakes": 0,
                            "delay": 3000
                        }
                    ]
                }),
                content_type='application/json'
            )
            update_words_request_word2.user = self.user
            word2_response = views.update_words(update_words_request_word2)
            self.assertEqual(json.loads(word2_response.content)['errors'][0]['code'], consts.TOO_EARLY_CODE)
            freeze_datetime.tick(delta=datetime.timedelta(days=1))
            word2_response = views.update_words(update_words_request_word2)
            self.assertEqual(json.loads(word2_response.content)['words'][0]['repetitionTime'], 1)


class FlashCardsIgnoreTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpassword',
                                             timezone='Europe/Moscow')
        self.packet1, next_pk = create_test_word_packet(1, 3, 0)
        UserLesson.objects.create(user=self.user, lesson=self.packet1.lesson)
        user_word_ignore = UserWordIgnore.objects.create(
            user=self.user,
            word=self.packet1.word_set.first()
        )
        self.ignored_word = user_word_ignore.word

    def test1(self):
        get_words_request = self.factory.get(path=reverse('dictionary:get_words', args=[self.packet1.pk]))
        get_words_request.user=self.user
        get_words_response = views.get_words(get_words_request, self.packet1.pk)
        data = json.loads(get_words_response.content)
        self.assertTrue(not self.ignored_word.pk in [d['pk'] for d in data['words']], 'get_words returning ignored word')

    def test2(self):
        UserWordRepetition.objects.create(
            word=self.ignored_word,
            user=self.user,
            repetition_datetime=timezone.now().replace(day=timezone.now().day - 1)
        )
        get_repetitions_request = self.factory.get(path=reverse('dictionary:get_repetitions'))
        get_repetitions_request.user = self.user
        get_repetitions_response = views.get_repetition_words(get_repetitions_request)
        data = json.loads(get_repetitions_response.content)
        self.assertTrue(not self.ignored_word.pk in [d['pk'] for d in data['words']], 'get_repetitions returning ignored word')
