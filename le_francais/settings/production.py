from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SECRET_KEY = os.environ.get('SECRET_KEY','8_83ey7rv$u_@t79klk$mp%#l)sol#uq2(@zj(@*$7o^3dpy21')

# Django Email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
	from .local import *
except ImportError:
	pass
