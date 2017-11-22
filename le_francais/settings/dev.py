from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
COMPRESS_ENABLED = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

ADMINS = [('semyon', 'semyon@atamas.com')]



try:
    from .local import *
except ImportError:
    pass
