import jwt
import datetime
import requests
from django.conf import settings

def get_signed_token(aud:str):
    with open('le_francais.pem', 'r') as key_file:
        private_key = key_file.read()
    payload = {
        'iss': 'www.le-francais.ru',
        'aud': aud,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
    }
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token

def get_courses_packets(user_id, cross_site_name):
    token = get_signed_token(cross_site_name)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{settings.COURSES_BASE_URL}/{settings.COURSES_FETCH_PACKETS_PATH.format(user_id)}',
                            headers=headers)
    data = response.json()
    if data.get('success', False):
        return data.get('packets', [])
    else:
        return []