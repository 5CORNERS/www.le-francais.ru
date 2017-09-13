from __future__ import absolute_import, unicode_literals

DEBUG = False
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Django Email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
	from .local import *
except ImportError:
	pass
