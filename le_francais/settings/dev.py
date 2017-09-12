from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8_83ey7rv$u_@t79klk$mp%#l)sol#uq2(@zj(@*$7o^3dpy21'

ADMINS = [('semyon', 'semyon@atamas.com')]

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST', True)
EMAIL_PORT = os.environ.get('EMAIL_PORT', True)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', True)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', True)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)

try:
    from .local import *
except ImportError:
    pass
