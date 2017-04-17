from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

try:
    from .local import *
except ImportError:
    pass
