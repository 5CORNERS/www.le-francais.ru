import json
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from le_francais_dictionary.views import UpdateUserStandalonePacketView
from le_francais_dictionary.models import UserStandalonePacket

User = get_user_model()

class UpdateUserStandalonePacketTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="testuser")
        
    def test_update_user_standalone_packet_success(self):
        with patch('le_francais_dictionary.views.jwt.decode') as mock_decode, \
             patch('le_francais_dictionary.views.load_courses_public_key') as mock_load_key:
            
            mock_decode.return_value = {"user_id": self.user.pk}
            mock_load_key.return_value = "fake_pub_key"
            
            data = {"words": [10, 20]}
            request = self.factory.post(
                '/some-url/', 
                data=json.dumps(data), 
                content_type='application/json',
                HTTP_AUTHORIZATION='Bearer fake_jwt_token'
            )
            
            view = UpdateUserStandalonePacketView.as_view()
            response = view(request)
            
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.content)
            self.assertTrue(response_data.get("success"))
            
            packet = UserStandalonePacket.objects.get(user=self.user)
            self.assertEqual(packet.words, [10, 20])
