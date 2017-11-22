from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SECRET_KEY = os.environ.get('SECRET_KEY')

# Django Email settings


try:
	from .local import *
except ImportError:
	pass
