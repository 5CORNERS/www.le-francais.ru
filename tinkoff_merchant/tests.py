import json

import mock
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from custom_user.models import User
from .models import Payment, Receipt, ReceiptItem
from .services import MerchantAPI

TEST_TERMINAL_KEY = '1508852342226'
TEST_SECRET_KEY = '123456'
TEST_CHECK_TOKEN = 'fb3a88515c7be9439a4eceac6c08b679c640d34e78899848edfab1adf10f9bb0'


def get_test_merchant_api():
    return MerchantAPI(terminal_key='1525120204909DEMO', secret_key='r8wft99b2dgje74c')


class PaymentsTestCase(TestCase):
    @mock.patch('tinkoff_merchant.views.Notification._merchant_api', get_test_merchant_api())
    def test_notification(self):
        payment, is_created = Payment.objects.get_or_create(order_id='12', amount=35000, payment_id='22461408', customer_key='763')

        notification = {
            'Success': True,
            'TerminalKey': '1525120204909DEMO',
            'Status': 'CONFIRMED',
            'ExpDate': '1122',
            'CardId': 4842090,
            'Pan': '430000******0777',
            'Amount': 35000,
            'PaymentId': 22461408,
            'OrderId': '12',
            'Token': 'a4a2fb3deb915437e4df09669f66d7cf69e61af84e4805c01200f62589c02922',
            'ErrorCode': '0',
        }

        resp = Client().post(
            reverse('tinkoff_payment:notification'), json.dumps(notification), content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b'OK')

        payment.refresh_from_db()

        self.assertEqual(payment.status, 'CONFIRMED')
        self.assertTrue(payment.success)
