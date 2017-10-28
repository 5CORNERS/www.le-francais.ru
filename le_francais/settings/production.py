from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SECRET_KEY = os.environ.get('SECRET_KEY')

# Django Email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
	from .local import *
except ImportError:
	pass
