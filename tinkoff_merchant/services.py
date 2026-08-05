import hashlib
import json
import types
import os
import certifi

import requests
from django.utils import timezone

from .consts import PAYMENT_STATUS_CONFIRMED
from .utils import Encoder
from .models import Payment
from .settings import get_config
from datetime import datetime, timedelta
from .signals import payment_refund


def get_ca_bundle_path():
    certs_dir = os.path.join(os.path.dirname(__file__), 'certs')
    combined_ca_path = os.path.join(certs_dir, 'combined_ca.pem')
    
    try:
        need_generate = not os.path.exists(combined_ca_path)
        
        # Discover all available certificate files (.pem and .crt) except the target output file itself
        cert_files = []
        if os.path.exists(certs_dir):
            for filename in os.listdir(certs_dir):
                if (filename.endswith('.pem') or filename.endswith('.crt')) and filename != 'combined_ca.pem':
                    cert_files.append(os.path.join(certs_dir, filename))
        
        # Check if any certificate file is newer than the generated combined_ca.pem
        if not need_generate and cert_files:
            combined_mtime = os.path.getmtime(combined_ca_path)
            for cert_path in cert_files:
                if os.path.getmtime(cert_path) > combined_mtime:
                    need_generate = True
                    break
        
        if need_generate:
            with open(certifi.where(), 'r', encoding='utf-8') as f:
                default_certs = f.read()
            
            custom_certs_list = []
            for cert_path in cert_files:
                try:
                    with open(cert_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if '-----BEGIN CERTIFICATE-----' in content:
                            # Normalize newline endings and append
                            custom_certs_list.append(content.strip())
                except Exception:
                    pass
            
            combined_certs = default_certs + '\n\n' + '\n\n'.join(custom_certs_list)
            with open(combined_ca_path, 'w', encoding='utf-8') as f:
                f.write(combined_certs)
    except Exception:
        custom_ca_path = os.path.join(certs_dir, 'russiantrustedca.pem')
        if os.path.exists(custom_ca_path):
            return custom_ca_path
        return certifi.where()
    
    return combined_ca_path



class PaymentHTTPException(Exception):
    pass


class MerchantAPI:
    _terminal_key = None
    _secret_key = None

    def __init__(self, terminal_key: str = None, secret_key: str = None):
        self._terminal_key = terminal_key
        self._secret_key = secret_key

    @property
    def secret_key(self):
        if not self._secret_key:
            self._secret_key = get_config()['SECRET_KEY']
        return self._secret_key

    @property
    def terminal_key(self):
        if not self._terminal_key:
            self._terminal_key = get_config()['TERMINAL_KEY']
        return self._terminal_key

    def _request(self, url: str, method: types.FunctionType, data: dict, p:Payment=None) -> requests.Response:
        url = get_config()['URLS'][url]

        data.update({
            'TerminalKey': self.terminal_key,
            'Token': self._token(data),
        })

        verify_config = get_config().get('VERIFY', True)
        if verify_config is True:
            verify = get_ca_bundle_path()
        else:
            verify = verify_config

        r = method(url, data=json.dumps(data, cls=Encoder), headers={'Content-Type': 'application/json'}, verify=verify)

        if r.status_code != 200:
            raise PaymentHTTPException('bad status code')

        if p is not None:
            p.request_history.append(dict(datetime=str(datetime.now()), url=url, data=data))
            p.save(update_fields=['request_history'])

        return r

    def _token(self, data: dict) -> str:
        base = [
            ['Password', self.secret_key],
        ]

        if 'TerminalKey' not in data:
            base.append(['TerminalKey', self.terminal_key])

        for k, v in data.items():
            if k in ['Token', 'Shops', 'Receipt', 'DATA']:
                continue
            if isinstance(v, bool):
                base.append([k, str(v).lower()])
            elif not isinstance(v, list) or not isinstance(v, dict):
                base.append([k, v])

        base.sort(key=lambda i: i[0])
        values = ''.join(map(lambda i: str(i[1]), base))

        m = hashlib.sha256()
        m.update(values.encode())
        return m.hexdigest()

    @staticmethod
    def update_payment_from_response(p: Payment, response: dict) -> Payment:
        for resp_field, model_field in Payment.RESPONSE_FIELDS.items():
            if resp_field in response:
                setattr(p, model_field, response.get(resp_field))
        p.status_history.append(dict(status=response.get('Status'), datetime=str(datetime.now())))
        p.response_history.append(dict(response=response, datetime=str(datetime.now())))
        return p

    def token_correct(self, token: str, data: dict) -> bool:
        return token == self._token(data)

    def init(self, p: Payment, data=None) -> Payment:
        if p.redirect_due_date is None:
            link_ttl_days = get_config()['TTL_DAYS']
            link_ttl_minutes = get_config()['TTL_MINUTES']
            p.redirect_due_date = (
                        timezone.now() + timedelta(days=link_ttl_days,  minutes=link_ttl_minutes))
        response = self._request('INIT', requests.post, p.to_json(data), p).json()
        return self.update_payment_from_response(p, response)

    def status(self, p: Payment) -> Payment:
        response = self._request('GET_STATE', requests.post, {'PaymentId': p.payment_id}, p).json()
        return self.update_payment_from_response(p, response)

    def cancel(self, p: Payment) -> Payment:
        response = self._request('CANCEL', requests.post, {'PaymentId': p.payment_id}, p).json()
        if p.status == PAYMENT_STATUS_CONFIRMED:
            payment_refund.send(self.__class__, payment=p)
        return self.update_payment_from_response(p, response)

    def charge(self, p: Payment) -> Payment:
        if p.parent is None:
            raise ValueError(f'parent field should be int, not None')
        response = self._request('CHARGE', requests.post, {
            'PaymentId': p.payment_id,
            'RebillId': p.parent.rebill_id,
            'SendEmail': True,
            'InfoEmail': p.email,
        }, p).json()
        return self.update_payment_from_response(p, response)
