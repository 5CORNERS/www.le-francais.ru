import json
import types

import requests
from django.conf import settings

from tinkoff_merchant.models import Payment
from tinkoff_merchant.utils import Encoder

TAX = 1
RECEIPT = 1
REFUND = 2


class Pay54Exception(Exception):
	pass


class Pay34API:
	_client_id = None
	_client_secret = None
	_test_enable = None

	def __init__(self, client_id: str = None, client_secret: str = None, test_enable: bool = None):
		self._client_id = client_id
		self._client_secret = client_secret
		self._test_enable = test_enable

	@property
	def client_id(self):
		if not self._client_id:
			self._client_id = settings.PAY54_CLIENT_ID
		return self._client_id

	@property
	def client_secret(self):
		if not self._client_secret:
			self._client_secret = settings.PAY54_CLIENT_SECRET
		return self._client_secret

	@property
	def test_enable(self):
		if not self._test_enable:
			self._test_enable = settings.PAY54_TEST_ENABLE
		return self._test_enable

	def _request(self, method: types.FunctionType, data: dict):
		url = "https://api.pay54.ru/receipt?client_id={0}&client_secret={1}".format(self.client_id, self.client_secret)
		if self.test_enable:
			url += '&test=1'
		response = method(url, data=json.dumps(data, cls=Encoder), headers={'Content-Type': 'application/json'})
		if response.status_code != 200:
			raise Pay54Exception('bad status code')

		return response

	def send_receipt_request(self, p: Payment):
		response = self._request(requests.post, p.receipt.to_json_pay54(receipt_type=RECEIPT, tax_type=TAX)).json()
		if response.get('error') == 1:
			raise Pay54Exception('Pay54 return error on receipt request\nerror message: ' + response.get('errorMessage') + '\nreceiptId: ' + str(response.get('receiptId')))
		else:
			return

	def send_refund_request(self, p: Payment):
		response = self._request(requests.post, p.receipt.to_json_pay54(receipt_type=REFUND, tax_type=TAX)).json()
		if response.get('error') == 1:
			raise Pay54Exception('Pay54 return error on refund request\nerror message: ' + response.get('errorMessage') + '\nreceiptId: ' + str(response.get('receiptId')))
		else:
			return
