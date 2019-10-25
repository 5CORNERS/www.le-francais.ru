import datetime
import json
import random

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from le_francais_dictionary.views import update_words
from wagtail.core.models import Page
from home.models import LessonPage
from .models import Word, WordTranslation, Packet, UserPacket, UserWordData, UserWordRepetition
from . import views

from django.contrib.auth import get_user_model

User = get_user_model()


def tick_10_seconds(frozen_time):
	frozen_time.tick(delta=datetime.timedelta(seconds=10))


class WordUserTestCase(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create_user(username='user1',
		                                     email='user1@email.com',
		                                     password='password')
		self.lesson1 = Page()
		self.lesson2 = LessonPage.objects.create(slug='lesson2', title='lesson2', lesson_number=2)
		self.packet1 = Packet.objects.create(name='packet1', lesson=self.lesson1)
		self.packet2 = Packet.objects.create(name='packet2', lesson=self.lesson2)
		self.word1 = Word.objects.create(word='word1', packet=self.packet1)
		self.word2 = Word.objects.create(word='word2', packet=self.packet1)
		self.word3 = Word.objects.create(word='word3', packet=self.packet2)
		self.word4 = Word.objects.create(word='word4', packet=self.packet2)
		self.translation2 = WordTranslation.objects.create(word=self.word2,
		                                                   translation='translation2')
		self.update_datetime = timezone.now()

	def test_add_packets(self):
		data = dict(
			packets=[self.packet1.pk, self.packet2.pk]
		)
		request = self.factory.post(reverse('dictionary:add_packets'),
		                            data=json.dumps(data),
		                            content_type='application/json')
		request.user = self.user
		response = views.add_packets(request)
		self.assertDictEqual(
			json.loads(response.content),
			dict(
				added=[self.packet1.pk, self.packet2.pk],
				already_exist=[],
			))

	def test_get_progress(self):
		user_packet = UserPacket.objects.create(packet=self.packet1,
		                                        user=self.user)
		request = self.factory.get(reverse('dictionary:get_progress'))
		request.user = self.user
		response = views.get_progress(request)
		self.assertJSONEqual(
			response.content,
			json.dumps({'packets': [dict(
				pk=user_packet.packet_id,
				name=user_packet.packet.name,
				activated=False,
				added=True,
				wordsCount=2,
				wordsLearned=0
			)]})
		)

	def test_get_progress_2(self):
		data = dict(
			packets=[self.packet1.pk, self.packet2.pk]
		)
		add_packet_request = self.factory.post(
			reverse('dictionary:add_packets'), data=json.dumps(data),
			content_type='application/json')
		add_packet_request.user = self.user
		views.add_packets(add_packet_request)

		get_progress_request = self.factory.get(
			reverse('dictionary:get_progress'))
		get_progress_request.user = self.user
		get_progress_response = views.get_progress(get_progress_request)
		self.assertJSONEqual(
			get_progress_response.content,
			json.dumps({'packets': [dict(
				pk=self.packet1.pk,
				name=self.packet1.name,
				activated=False,
				added=True,
				wordsCount=2,
				wordsLearned=0,
			), dict(
				pk=self.packet2.pk,
				name=self.packet2.name,
				activated=False,
				added=True,
				wordsCount=2,
				wordsLearned=0,
			)]})
		)

	def test_update_words(self):
		initial_datetime = datetime.datetime(1,1,1,12,0,0)

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
						frozen_datetime.tick(delta=datetime.timedelta(seconds=10))
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
					if UserWordRepetition.objects.filter(repetition_date__gt=timezone.now()):
						frozen_datetime.tick(delta=datetime.timedelta(days=1))
					else:
						passing = False
