from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8_83ey7rv$u_@t79klk$mp%#l)sol#uq2(@zj(@*$7o^3dpy21'

ADMINS = [('semyon', 'semyon@atamas.com')]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
