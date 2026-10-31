import datetime
import jwt
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from user_sessions.models import Session
from le_francais_dictionary.models import Packet, VerbPacket, Verb, VerbPacketRelation
from le_francais_dictionary.utils import login_from_courses_token

User = get_user_model()


class SSOEmbedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='embeduser', email='embed@example.com', password='password123')
        self.factory = RequestFactory()
        # Read courses private key from courses repo to sign test tokens
        with open(r'C:\Users\anton\PycharmProjects\courses-le-francais\private.pem', 'r') as f:
            self.private_key = f.read()

    def _make_token(self, user_id, expired=False):
        now = datetime.datetime.now(datetime.timezone.utc)
        exp = now - datetime.timedelta(minutes=5) if expired else now + datetime.timedelta(minutes=5)
        payload = {
            'user_id': user_id,
            'aud': 'www.le-francais.ru',
            'iss': 'courses.le-francais.ru',
            'iat': now,
            'exp': exp,
        }
        return jwt.encode(payload, self.private_key, algorithm='RS256')

    def test_login_from_courses_token_success_creates_session_record(self):
        token = self._make_token(self.user.pk)
        request = self.factory.get(f'/?token={token}')
        from le_francais.middleware import CustomSessionMiddleware
        middleware = CustomSessionMiddleware()
        middleware.process_request(request)

        logged_user = login_from_courses_token(request)
        self.assertEqual(logged_user, self.user)
        self.assertTrue(request.user.is_authenticated)

        session_key = request.session.session_key
        self.assertTrue(session_key)
        self.assertTrue(Session.objects.filter(session_key=session_key, user=self.user).exists())

    def test_login_from_courses_token_already_logged_in_no_rotation(self):
        token = self._make_token(self.user.pk)
        request = self.factory.get(f'/?token={token}')
        from le_francais.middleware import CustomSessionMiddleware
        middleware = CustomSessionMiddleware()
        middleware.process_request(request)

        # First login
        login_from_courses_token(request)
        first_key = request.session.session_key

        # Second login call with same user should not rotate session key
        logged_user = login_from_courses_token(request)
        self.assertEqual(logged_user, self.user)
        self.assertEqual(request.session.session_key, first_key)

    def test_login_from_courses_token_expired_noop(self):
        token = self._make_token(self.user.pk, expired=True)
        request = self.factory.get(f'/?token={token}')
        from le_francais.middleware import CustomSessionMiddleware
        middleware = CustomSessionMiddleware()
        middleware.process_request(request)

        logged_user = login_from_courses_token(request)
        self.assertIsNone(logged_user)
        self.assertFalse(request.user.is_authenticated)

    def test_open_verbs_iframe_logs_in_and_does_not_leak_token_in_redirect(self):
        packet = Packet.objects.create(name='Test Packet')
        token = self._make_token(self.user.pk)
        url = reverse('dictionary:verbs_iframe', kwargs={'packet_id': packet.pk}) + f'?token={token}'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Verify user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        # Verify redirect Location does not contain token
        location = response['Location']
        self.assertNotIn('token=', location)
        self.assertNotIn(token, location)
