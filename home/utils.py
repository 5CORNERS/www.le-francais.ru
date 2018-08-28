from collections import defaultdict
import binascii
from hashlib import md5

from django.conf import settings


def get_signature(params, secret_key=settings.WALLET_ONE_SECRET_KEY):
    """
    Base64(Byte(MD5(Windows1251(Sort(Params) + SecretKey))))
    params - list of tuples [('WMI_CURRENCY_ID', 643), ('WMI_PAYMENT_AMOUNT', 10)]
    """
    icase_key = lambda s: str(s).lower()

    lists_by_keys = defaultdict(list)
    for key, value in params:
        lists_by_keys[key].append(value)

    str_buff = b''
    for key in sorted(lists_by_keys, key=icase_key):
        for value in sorted(lists_by_keys[key], key=icase_key):
            str_buff += str(value).encode('1251')
    str_buff += secret_key.encode('1251')

    md5_string = md5(str_buff).digest()
    return binascii.b2a_base64(md5_string)[:-1]