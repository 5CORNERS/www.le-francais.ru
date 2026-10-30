import json
from unittest.mock import patch, MagicMock
import requests
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from le_francais.courses_client import get_courses_packets
from le_francais_dictionary.forms import WordsManagementFilterForm
from le_francais_dictionary.models import Packet

User = get_user_model()


class CoursesClientTest(TestCase):
    def test_get_courses_packets_none_user_id(self):
        # Should return empty list immediately without making any HTTP requests
        with patch('requests.get') as mock_get:
            result = get_courses_packets(None, 'courses.le-francais.ru')
            self.assertEqual(result, [])
            mock_get.assert_not_called()

    def test_get_courses_packets_empty_user_id(self):
        with patch('requests.get') as mock_get:
            result = get_courses_packets('', 'courses.le-francais.ru')
            self.assertEqual(result, [])
            mock_get.assert_not_called()

    @patch('le_francais.courses_client.get_signed_token', return_value='fake-token')
    @patch('requests.get')
    def test_get_courses_packets_html_error_response(self, mock_get, mock_token):
        # Simulates 404 returning HTML (the exact bug that caused JSONDecodeError)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.text = "\n<!DOCTYPE html><html><body>Not Found</body></html>"
        mock_response.json.side_effect = json.decoder.JSONDecodeError("Expecting value", mock_response.text, 1)
        mock_get.return_value = mock_response

        result = get_courses_packets(123, 'courses.le-francais.ru')
        self.assertEqual(result, [])

    @patch('le_francais.courses_client.get_signed_token', return_value='fake-token')
    @patch('requests.get')
    def test_get_courses_packets_network_error(self, mock_get, mock_token):
        # Simulates connection error / timeout
        mock_get.side_effect = requests.RequestException("Connection refused")

        result = get_courses_packets(123, 'courses.le-francais.ru')
        self.assertEqual(result, [])

    @patch('le_francais.courses_client.get_signed_token', return_value='fake-token')
    @patch('requests.get')
    def test_get_courses_packets_success(self, mock_get, mock_token):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {'success': True, 'packets': [3416, 3417]}
        mock_get.return_value = mock_response

        result = get_courses_packets(123, 'courses.le-francais.ru')
        self.assertEqual(result, [3416, 3417])


class WordsManagementFilterFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='authuser', email='test@example.com')
        self.packet = Packet.objects.create(name='Test Packet', cross_site_available=True, cross_site_id=13)

    def test_anonymous_user_with_cross_site(self):
        # Anonymous user should not call get_courses_packets and have empty packets queryset
        with patch('le_francais_dictionary.forms.get_courses_packets') as mock_client:
            form = WordsManagementFilterForm(AnonymousUser(), cross_site='courses')
            self.assertEqual(list(form.packets), [])
            mock_client.assert_not_called()

    def test_invalid_cross_site_key_does_not_raise_key_error(self):
        # Invalid cross_site key should not crash with KeyError
        form = WordsManagementFilterForm(AnonymousUser(), cross_site='unknown_domain_key')
        self.assertEqual(list(form.packets), [])

    @patch('le_francais_dictionary.forms.get_courses_packets', return_value=[])
    def test_authenticated_user_with_cross_site(self, mock_client):
        form = WordsManagementFilterForm(self.user, cross_site='courses')
        mock_client.assert_called_once_with(self.user.pk, 'courses.le-francais.ru')
        self.assertEqual(list(form.packets), [])


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ManageWordsStandaloneViewTest(TestCase):
    def setUp(self):
        self.packet = Packet.objects.create(pk=3416, name='Test Packet 3416', cross_site_available=True, cross_site_id=13)

    def test_anonymous_request_standalone_zero(self):
        # Exact reproduction of the user request: /dictionary/my-words-standalone/0/?p=3416&ck=courses
        response = self.client.get('/dictionary/my-words-standalone/0/?p=3416&ck=courses')
        self.assertEqual(response.status_code, 200)

    def test_invalid_p_query_param_does_not_crash(self):
        response = self.client.get('/dictionary/my-words-standalone/0/?p=not-a-number&ck=courses')
        self.assertEqual(response.status_code, 200)


class PacketIsActivatedTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='paiduser', email='paid@example.com')
        self.user.must_pay = True
        self.user.save()

        self.packet = Packet.objects.create(
            pk=101,
            name='Cross Site Packet',
            cross_site_available=True,
            cross_site_id=20,
            cross_site_site_name='courses'
        )

    @patch('le_francais_dictionary.models.get_courses_packets', return_value=[101])
    def test_cross_site_packet_activated_when_in_courses_packets(self, mock_get_packets):
        self.assertTrue(self.packet.is_activated(self.user))
        mock_get_packets.assert_called_once_with(self.user.pk, 'courses.le-francais.ru')

    @patch('le_francais_dictionary.models.get_courses_packets', return_value=[999])
    def test_cross_site_packet_not_activated_when_not_in_courses_packets(self, mock_get_packets):
        self.assertFalse(self.packet.is_activated(self.user))
        mock_get_packets.assert_called_once_with(self.user.pk, 'courses.le-francais.ru')

    @patch('le_francais_dictionary.models.get_courses_packets')
    def test_cross_site_packet_anonymous_user(self, mock_get_packets):
        self.assertFalse(self.packet.is_activated(AnonymousUser()))
        mock_get_packets.assert_not_called()

    @patch('le_francais_dictionary.models.get_courses_packets')
    def test_cross_site_packet_none_user(self, mock_get_packets):
        self.assertFalse(self.packet.is_activated(None))
        mock_get_packets.assert_not_called()

    @patch('le_francais_dictionary.models.get_courses_packets', return_value=[])
    def test_user_not_must_pay_is_activated(self, mock_get_packets):
        self.user.must_pay = False
        self.user.save()
        self.assertTrue(self.packet.is_activated(self.user))

    def test_non_cross_site_packet(self):
        regular_packet = Packet.objects.create(name='Regular Packet')
        self.assertFalse(regular_packet.is_activated(self.user))

