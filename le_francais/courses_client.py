import jwt
import datetime
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

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
    if not user_id or not cross_site_name:
        return []
    try:
        token = get_signed_token(cross_site_name)
        headers = {'Authorization': f'Bearer {token}'}
        url = f'{settings.COURSES_BASE_URL}{settings.COURSES_FETCH_PACKETS_PATH.format(user_id)}'
        response = requests.get(url, headers=headers, timeout=5)
        if not response.ok:
            logger.warning(f"Failed to fetch courses packets for user {user_id}: HTTP {response.status_code}")
            return []
        data = response.json()
        if data.get('success', False):
            return data.get('packets', [])
        else:
            return []
    except (requests.RequestException, ValueError, Exception) as e:
        logger.warning(f"Error fetching courses packets for user {user_id}: {e}")
        return []
