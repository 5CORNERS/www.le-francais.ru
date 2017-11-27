from django.test import TestCase, Client

from custom_user.models import User


class ChangeUsernameTestCase(TestCase):
	def setUp(self):
		User.objects.create(username='username1', email='username1@example.com', password='password1')
		User.objects.create(username='username2', email='username2@example.com', password='password2')

	def test_change_username(self):
		c = Client()
		c.login(username='username1', password='password1')
		c.post('/accaunts/username/change', {'username':'username3'})
		self.assertEqual(User.objects.get(email='username1@example.com').username, 'username3')