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
    if len(params[0]) == 3:
        for key, value, id in params:
            lists_by_keys[key].append(value)
    else:
        for key, value in params:
            lists_by_keys[key].append(value)

    str_buff = b''
    for key in sorted(lists_by_keys, key=icase_key):
        for value in sorted(lists_by_keys[key], key=icase_key):
            str_buff += str(value).encode('1251')
    str_buff += secret_key.encode('1251')

    md5_string = md5(str_buff).digest()
    return (binascii.b2a_base64(md5_string)[:-1])

def message_left(n, form1='чашечка', form2='чашечки', form5='чашечек'):
    n10 = n%10
    n100 = n%100
    if n == 0:
        return 'У Вас не осталось {0} :('.format(form5)
    elif n10 == 1 and n100 != 11:
        return 'У вас есть ещё {0} {1}. Просмотреть свой остаток и пополнить запас вы можете в настройках профиля.'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return 'У вас есть ещё {0} {1}. Просмотреть свой остаток и пополнить запас вы можете в настройках профиля.'.format(str(n), form2)
    else:
        return 'У вас есть ещё {0} {1}. Просмотреть свой остаток и пополнить запас вы можете в настройках профиля.'.format(str(n), form5)

def message(n, form1=' чашечка', form2=' чашечки', form5=' чашечек'):
    n10 = n % 10
    n100 = n % 100
    if n10 == 1 and n100 != 11:
        return '{0} {1}'.format(str(n), form1)
    elif n10 in [2, 3, 4] and n100 not in [12, 13, 14]:
        return '{0} {1}'.format(str(n), form2)
    else:
        return '{0} {1}'.format(str(n), form5)