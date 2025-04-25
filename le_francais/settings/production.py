from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_MAX_AGE = 31557600

WHITENOISE_KEEP_ONLY_HASHED_FILES = False

def add_header_service_worker_allowed(headers, path, url):
    if path.endswith('.js'):
        headers['Service-Worker-Allowed'] = '/'

WHITENOISE_ADD_HEADERS_FUNCTION = add_header_service_worker_allowed

ALLOWED_HOSTS = [
    'www.le-francais.ru',
    # os.environ.get('HEROKU_APP_NAME', 'none')+'.herokuapp.com'
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

SESSION_COOKIE_DOMAIN = '.le-francais.ru'

try:
	from .local import *
except ImportError:
	pass
