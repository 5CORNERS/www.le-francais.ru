import jwt
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from custom_user.models import User
from user_sessions.models import Session
from django.utils import timezone
from datetime import timedelta


class AuthAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

        # We need to mock the JWT token that courses app will send.
        # Since IsValidCourses reads 'courses_public.pem', we'll bypass the JWT decode directly in test,
        # or we mock IsValidCourses.has_permission. Let's mock the permission class.
        from unittest.mock import patch
        self.patcher = patch('le_francais.permsissions.IsValidCourses.has_permission', return_value=True)
        self.mock_has_permission = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_login_success(self):
        url = reverse('api-login')
        data = {'identifier': 'test@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_login_failure(self):
        url = reverse('api-login')
        data = {'identifier': 'test@example.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_success(self):
        url = reverse('api-register')
        data = {'username': 'newuser', 'email': 'new@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_register_duplicate_email(self):
        url = reverse('api-register')
        data = {'username': 'anotheruser', 'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_session_retrieval_success(self):
        session = Session.objects.create(
            session_key='testsessionkey',
            user=self.user,
            expire_date=timezone.now() + timedelta(days=1)
        )
        url = reverse('api-session', kwargs={'session_id': 'testsessionkey'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_session_retrieval_expired(self):
        session = Session.objects.create(
            session_key='expiredsession',
            user=self.user,
            expire_date=timezone.now() - timedelta(days=1)
        )
        url = reverse('api-session', kwargs={'session_id': 'expiredsession'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)