from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
COMPRESS_ENABLED = True
REQUEST_ID_HEADER = None

ALLOWED_HOSTS = ALLOWED_HOSTS + [
	'localhost','le-francais.ru'
]

# STATICFILES_STORAGE = 'django.core.files.storage.FileSystemStorage'


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_MAX_AGE = 31557600

WHITENOISE_KEEP_ONLY_HASHED_FILES = False

def add_header_service_worker_allowed(headers, path, url):
    if path.endswith('.js'):
        headers['Service-Worker-Allowed'] = '/'

WHITENOISE_ADD_HEADERS_FUNCTION = add_header_service_worker_allowed

try:
	from .local import *
except ImportError:
	pass
