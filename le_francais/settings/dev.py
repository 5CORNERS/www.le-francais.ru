from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
COMPRESS_ENABLED = True
REQUEST_ID_HEADER = None

try:
	from .local import *
except ImportError:
	pass

ALLOWED_HOSTS = ALLOWED_HOSTS + [
	'le-francais.ru',
	'localhost',
	'127.0.0.1',
	'192.168.0.27',
]

# STATICFILES_STORAGE = 'django.core.files.storage.FileSystemStorage'


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_MAX_AGE = 31557600

WHITENOISE_KEEP_ONLY_HASHED_FILES = False

def add_header_service_worker_allowed(headers, path, url):
    if path.endswith('.js'):
        headers['Service-Worker-Allowed'] = '/'

WHITENOISE_ADD_HEADERS_FUNCTION = add_header_service_worker_allowed
