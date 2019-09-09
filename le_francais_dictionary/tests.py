import json

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from .models import Word, WordTranslation, Packet, UserPacket
from . import views

from django.contrib.auth import get_user_model

User = get_user_model()

class WordUserTestCase(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create_user(username='user1', email='user1@email.com', password='password')
		self.packet1 = Packet.objects.create(name='packet1')
		self.packet2 = Packet.objects.create(name='packet2')
		self.word1 = Word.objects.create(word='word1', packet=self.packet1)
		self.word2 = Word.objects.create(word='word2', packet=self.packet1)
		self.word3 = Word.objects.create(word='word3', packet=self.packet2)
		self.word4 = Word.objects.create(word='word4', packet=self.packet2)
		self.translation2 = WordTranslation.objects.create(word=self.word2, translation='translation2')
		self.update_datetime = timezone.now()

	def test_add_packets(self):
		data = dict(
			packets=[self.packet1.pk, self.packet2.pk]
		)
		request = self.factory.post(reverse('dictionary:add_packets'), data=json.dumps(data), content_type='application/json')
		request.user = self.user
		response = views.add_packets(request)
		self.assertDictEqual(
			json.loads(response.content),
			dict(
			    added=[self.packet1.pk, self.packet2.pk],
				already_exist=[],
			))

	def test_get_progress(self):
		user_packet = UserPacket.objects.create(packet=self.packet1, user=self.user)
		request = self.factory.get(reverse('dictionary:get_progress'))
		request.user = self.user
		response = views.get_progress(request)
		self.assertJSONEqual(
			response.content,
			json.dumps({'packets': [dict(
				pk=user_packet.packet_id,
				name=user_packet.packet.name,
				activated=True,
				added=True,
				wordsCount=2,
				wordsLearned=0
			)]})
		)
