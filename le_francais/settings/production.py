from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False
STATICFILES_STORAGE = 'le_francais.storage.WhiteNoiseStaticFilesStorage'

# Django Email settings


try:
	from .local import *
except ImportError:
	pass
