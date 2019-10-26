"""
Django settings for le_francais project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from __future__ import absolute_import, unicode_literals

import os
import sys

import dj_database_url
import dj_email_url

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'home',
    'search',
    'django_cron',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',
    'robots',

    'dal',
    'dal_select2',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.postgres',
    'bootstrapform',
    'django.core.mail',

    'annoying',
    'user_sessions',
    'corsheaders',

    'sass_processor',

    'storages',

    'social_django',
    'social_core',

    'allauth',
    'allauth.account',

    'snowpenguin.django.recaptcha3',

    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.vk',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.mailru',
    'allauth.socialaccount.providers.odnoklassniki',
    'svg',
    'custom_user',
    'pybb',
    'mailer',
    'postman',
    'forum',
    'forum_messages',
    'profiles',
    'pure_pagination',
    'captcha',
    'crispy_forms',
    'django_comments_xtd',
    'django_comments',
    'le_nombres',
    # 'django_mobile',
    'django_user_agents',
    'polly',
    'conjugation',
    'le_francais_dictionary',
    'notifications',

    'tinkoff_merchant',
    'django_js_reverse',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'le_francais.middleware.SessionHeaderMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    'pybb.middleware.PybbMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

    'django_user_agents.middleware.UserAgentMiddleware',
    # 'home.middleware.MobileTabletDetectionMiddleware',
    # 'home.middleware.CanonicalDomainMiddleware',
    # 'django_mobile.middleware.SetFlavourMiddleware',

    'custom_user.middleware.GetPush4SiteId',
]

SESSION_ENGINE = 'user_sessions.backends.db'
SESSION_SAVE_EVERY_REQUEST = True


ROOT_URLCONF = 'le_francais.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            'forum_messages/templates',
            'conjugation/templates'
        ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                "django.template.context_processors.i18n",
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'pybb.context_processors.processor',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'libraries': {
                'conjugation_tags': 'conjugation.templatetags.conjugation_tags',
            },
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )
        }
    }
]

TEMPLATE_LOADERS = TEMPLATES[0]['OPTIONS']['loaders']

WSGI_APPLICATION = 'le_francais.wsgi.application'

SECRET_KEY = os.environ.get('SECRET_KEY')

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT") == "True"

# Redirect only /accounts/*
# SECURE_REDIRECT_EXEMPT = [
#     '^(?!.*accounts).*$',
# ]

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

TESTING = 'test' in sys.argv[1:]
if TESTING:
    print('=========================')
    print('In TEST Mode')
    print('Disabling Migrations')
    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()
    print('Using Local Test Database')
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5433',
    }
    print('=========================\n')
else:
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)

DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520

# A list of authentication backend classes to use when attempting to authenticate a user.
AUTH_USER_MODEL = 'custom_user.User'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.yandex.YandexOAuth2',
    'social_core.backends.mailru.MailruOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.odnoklassniki.OdnoklassnikiOAuth2',

    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'le_francais.authentication.SessionAuthentication',
)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False
USE_TZ = True
SITE_ID = 1

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'forum_messages', 'locale'),
    os.path.join(BASE_DIR, 'home', 'locale')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

WHITENOISE_MAX_AGE = 31557600

# Sass Processor settings

SASS_PROCESSOR_AUTO_INCLUDE = False

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(BASE_DIR, 'home/static/scss'),
    # os.path.join(BASE_DIR, 'home/static/components'),
]

SASS_PRECISION = 8

SASS_OUTPUT_STYLE = 'compact'

# Amazon AWS S3 settings

AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000',
}
AWS_STORAGE_BUCKET_NAME = 'le-francais'
AWS_S3_REGION_NAME = 'eu-central-1'  # e.g. us-east-2
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# Amazon Polly settings

POLLY_OUTPUT_S3_BUCKET_NAME = 'le-francais'
POLLY_OUTPUT_S3_KEY_PREFIX = 'polly-conjugations/'

# Media settings

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/'

# Robots settings

ROBOTS_USE_SITEMAP = False
ROBOTS_USE_HOST = True

# PyBBM settings

PYBB_USE_DJANGO_MAILER = True

PYBB_FORUM_PAGE_SIZE = 60
PYBB_TOPIC_PAGE_SIZE = 20
PYBB_MARKUP_ENGINES_PATHS = {
    'custom_markdown': 'forum.markup_engines.CustomMarkdownParser'
}
PYBB_MARKUP = 'custom_markdown'
PYBB_BODY_CLEANERS = []
PYBB_BODY_VALIDATOR = None

PYBB_TEMPLATE = 'forum.html'
PYBB_NICE_URL = False

# disable pybb smiles
PYBB_SMILES = dict()
# disable auto subscribe
PYBB_DEFAULT_AUTOSUBSCRIBE = True
PYBB_DEFAULT_TITLE = 'Forum'
PYBB_PERMISSION_HANDLER = 'forum.permissions.CustomPermissionHandler'

# Postman settings

POSTMAN_AUTO_MODERATE_AS = True
POSTMAN_NAME_USER_AS = 'username'
POSTMAN_SHOW_USER_AS = 'username'
POSTMAN_DISALLOW_ANONYMOUS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'no_reply@files.le-francais.ru'

email_config = dj_email_url.config()

EMAIL_HOST = os.environ.get('EMAIL_HOST', email_config['EMAIL_HOST'])
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', email_config['EMAIL_PORT']))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', email_config['EMAIL_HOST_USER'])
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', email_config['EMAIL_HOST_PASSWORD'])
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', email_config['EMAIL_USE_TLS']) == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', email_config['EMAIL_USE_SSL']) == 'True'

# Django Mailer Settings

MAILER_EMAIL_MAX_BATCH = 20
MAILER_EMAIL_MAX_DEFERRED = 1
MAILER_EMAIL_THROTTLE = 20

# WalletOne settings

WALLET_ONE_MERCHANT_ID = os.environ.get('WALLET_ONE_MERCHANT_ID')
WALLET_ONE_SECRET_KEY = os.environ.get('WALLET_ONE_SECRET_KEY')

# Wagtail settings

WAGTAIL_SITE_NAME = "le_francais"

# Base URL to use when referring to full URLs within the Wagtail admin backend-
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'www.le-francais.ru'

ALLOWED_HOSTS = [
    'hidden-refuge-27954-bs-4.herokuapp.com',
    'www.le-francais.ru',
    'le-francais.ru',
    'localhost',
    '127.0.0.1',
    '192.168.0.27',
    os.environ.get('HEROKU_APP_NAME', 'none')+'.herokuapp.com'
]

X_FRAME_OPTIONS = os.environ.get('X_FRAME_OPTIONS', 'SAMEORIGIN')

# Allauth settings

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_FORM_CLASS = 'custom_user.forms.CaptchaAllauthSignupForm'

SOCIALACCOUNT_EMAIL_VERIFICATION = False
LOGIN_ERROR_URL = '/accounts/login/'

# Social-Auth settings
NEW_USER_REDIRECT_URL = '/accounts/username/change_new'
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_NEW_USER_REDIRECT = 'new-users-redirect-url/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/'
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    # 'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']

SOCIAL_AUTH_MAILRU_OAUTH2_SCOPE = ['nick']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_VK_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_VK_OAUTH2_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_VK_OAUTH2_SECRET')

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_YANDEX_OAUTH2_KEY')
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_YANDEX_OAUTH2_SECRET')

SOCIAL_AUTH_MAILRU_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_MAILRU_OAUTH2_KEY')
SOCIAL_AUTH_MAILRU_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_MAILRU_OAUTH2_SECRET')

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_FACEBOOK_API_VERSION = '2.10'

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email',
}
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_KEY')
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_SECRET')
SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_PUBLIC_NAME = os.environ.get('SOCIAL_AUTH_ODNOKLASSNIKI_OAUTH2_PUBLIC_NAME')

COMMENTS_APP = 'django_comments_xtd'
COMMENTS_XTD_MAX_THREAD_LEVEL = 999
COMMENTS_XTD_CONFIRM_EMAIL = True
COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'default': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    }
}

FLAVOURS = ('full', 'mobile', 'tablet')

# Tinkoff terminal api

TINKOFF_PAYMENTS_CONFIG = {
    'URLS': {
        'INIT': 'https://securepay.tinkoff.ru/v2/Init',
        'GET_STATE': 'https://securepay.tinkoff.ru/v2/GetState',
        'CANCEL': 'https://securepay.tinkoff.ru/v2/Cancel',
    },
    'TAXATION': 'usn_income',
    'ITEM_TAX': 'none',
    'TERMINAL_KEY': os.environ.get('TINKOFF_TERMINAL_ID'),
    'SECRET_KEY': os.environ.get('TINKOFF_TERMINAL_PASSWORD'),
}

# Pay34 settings

PAY54_CLIENT_ID = os.environ.get('PAY54_CLIENT_ID')
PAY54_CLIENT_SECRET = os.environ.get('PAY54_CLIENT_SECRET')
PAY54_TEST_ENABLE = False

# Js Reverse settings

JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['notifications', 'api']
JS_REVERSE_OUTPUT_PATH = 'home/static/django_js_reverse/js/'

# Logging settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
    },
}
# ReCaptcha V3 settings

RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5

# Corse Headers settings

CORS_ORIGIN_ALLOW_ALL = os.getenv('CORS_ORIGIN_ALLOW_ALL', 'False') == 'True'
