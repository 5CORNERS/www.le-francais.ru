from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8_83ey7rv$u_@t79klk$mp%#l)sol#uq2(@zj(@*$7o^3dpy21'

ADMINS = [('semyon', 'semyon@atamas.com')]

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = 'no_reply@files.le-francais.ru'
EMAIL_HOST = os.environ.get('EMAIL_HOST', "localhost")
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', "")
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', "")
EMAIL_USE_TLS =True if (os.environ.get('EMAIL_USE_TLS', False)) == 'True' else False
EMAIL_USE_SSL =True if (os.environ.get('EMAIL_USE_TLS', False)) == 'True' else False

try:
    from .local import *
except ImportError:
    pass
