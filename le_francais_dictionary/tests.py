import json

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from .models import UserWord, Word, WordTranslation
from . import views

from django.contrib.auth import get_user_model

User = get_user_model()

class WordUserTestCase(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create_user(username='user1', email='user1@email.com', password='password')
		self.word1 = Word.objects.create(word='word1')
		self.word2 = Word.objects.create(word='word2')
		self.translation2 = WordTranslation.objects.create(word=self.word2, translation='translation2')
		self.update_datetime = timezone.now()
		self.user_word1 = UserWord.objects.create(word=self.word2, user=self.user, update_datetime=self.update_datetime, stars=1)

	def test_userword_getting(self):
		request = self.factory.get(reverse('dictionary:get_user_words'))
		request.user = self.user
		response = views.get_user_words(request)
		response_dict = dict(
			words=[dict(
				pk=self.word2.pk,
				word=self.word2.word,
				pollyUrl=None,
				gender=None,
				partOfSpeech=None,
				plural=False,
				translations=[dict(
					translation=self.translation2.translation,
					pollyUrl=None
				)],
				userData=dict(
					datetime=self.update_datetime.isoformat(),
					stars=1
				)
			)]
		)
		self.assertDictEqual(json.loads(response.content), response_dict)

	def test_userword_creating(self):
		data = {'words':[self.word1.pk, self.word2.pk]}
		json_data = json.dumps(data)
		request = self.factory.post(reverse('dictionary:add_words'), data=json_data, content_type='application/json')
		request.user = self.user
		response = views.add_user_words(request)
		self.assertDictEqual(json.loads(response.content), dict(created=[self.word1.id], alreadyExist=[self.word2.id]))

	def test_userword_updating(self):
		data = {'words': [
			dict(pk=self.word2.id, stars=2),
		]}
		json_data = json.dumps(data)
		request = self.factory.post(reverse('dictionary:update_words'), data=json_data, content_type='application/json')
		request.user = self.user
		response = views.update_user_words(request)
		self.assertDictEqual(json.loads(response.content), dict(
			updated=[self.word2.id]
		))
