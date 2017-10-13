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

import dj_database_url

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
	'home',
	'search',
	'old_site',

	'wagtail.wagtailforms',
	'wagtail.wagtailredirects',
	'wagtail.wagtailembeds',
	'wagtail.wagtailsites',
	'wagtail.wagtailusers',
	'wagtail.wagtailsnippets',
	'wagtail.wagtaildocs',
	'wagtail.wagtailimages',
	'wagtail.wagtailsearch',
	'wagtail.wagtailadmin',
	'wagtail.wagtailcore',

	'modelcluster',
	'taggit',
	'robots',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.sites',
	'django.contrib.sitemaps',
	'bootstrapform',
	'django.core.mail',

	'allauth',
	'allauth.account',

	'allauth.socialaccount',
	'allauth.socialaccount.providers.google',
	'allauth.socialaccount.providers.vk',
	'allauth.socialaccount.providers.facebook',
	'allauth.socialaccount.providers.mailru',

	'custom_user',
	'pybb',
	'postman',
	'forum',
	'forum_messages',
	'profiles',
	'pure_pagination',
	'sorl.thumbnail',
	'captcha',
	'crispy_forms',

]

MIDDLEWARE_CLASSES = [
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.security.SecurityMiddleware',

	'wagtail.wagtailcore.middleware.SiteMiddleware',
	'wagtail.wagtailredirects.middleware.RedirectMiddleware',

	'pybb.middleware.PybbMiddleware',
	# 'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'le_francais.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [
			os.path.join(PROJECT_DIR, 'templates'),
		],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				"django.template.context_processors.i18n",
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',

				'pybb.context_processors.processor',
				# 'social_django.context_processors.backends',
				# 'social_django.context_processors.login_redirect',
			],
		},
	},
]

WSGI_APPLICATION = 'le_francais.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': 'mydatabase',
	}
}

db_from_env = dj_database_url.config(conn_max_age=500)

DATABASES['default'].update(db_from_env)

DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520

# A list of authentication backend classes to use when attempting to authenticate a user.
AUTH_USER_MODEL = 'custom_user.User'

AUTHENTICATION_BACKENDS = (
	# 'social_core.backends.google.GoogleOAuth2',
	# 'social_core.backends.vk.VKOAuth2',
	# 'social_core.backends.yandex.YandexOAuth2',
	# 'social_core.backends.mailru.MailruOAuth2',
	# 'social_core.backends.facebook.FacebookOAuth2',

	'django.contrib.auth.backends.ModelBackend',
	'allauth.account.auth_backends.AuthenticationBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False
USE_TZ = True
SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_FINDERS = [
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
	os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_URL = '/accounts/login'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/login/'

# Robots settings

ROBOTS_USE_SITEMAP = False
ROBOTS_USE_HOST = False

# PyBBM settings

PYBB_FORUM_PAGE_SIZE = 60
PYBB_TOPIC_PAGE_SIZE = 30
PYBB_MARKUP_ENGINES_PATHS = {
	'custom_markdown': 'forum.markup_engines.CustomMarkdownParser'
}
PYBB_MARKUP = 'custom_markdown'
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

# Wagtail settings

WAGTAIL_SITE_NAME = "le_francais"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = '192.168.0.27:8000'

ALLOWED_HOSTS = [
	'94.188.74.123',
	'hidden-refuge-27954.herokuapp.com',
	'www.le-francais.ru',
	'le-francais.ru',
	'hidden-refuge-27954.herokuapp.com',
	'localhost',
	'fe61337f.ngrok.io',
	'192.168.0.27'
]

# Allauth settings

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

SOCIALACCOUNT_PROVIDERS = {
	'facebook': {
		'METHOD': 'oauth2',
		'SCOPE': ['email', 'public_profile'],
		'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
		'INIT_PARAMS': {'cookie': True},
		'FIELDS': [
			'id',
			'email',
			'name',
			'first_name',
			'last_name',
			'verified',
			'locale',
			'timezone',
			'link',
			'gender',
			'updated_time',
		],
		'EXCHANGE_TOKEN': True,
		'LOCALE_FUNC': lambda request: 'en_US',
		'VERIFIED_EMAIL': False,
		'VERSION': 'v2.5',
	},
	'google': {
		'SCOPE': [
			'profile',
			'email',
		],
		'AUTH_PARAMS': {
			'access_type': 'online',
		}
	}
}

# Social-Auth settings

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/forum'
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

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '984233441228-m8un6479b9r2nr71f69ugvsh2mvjq981.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'Y0CiV0MWBUrGN-GsM_H9sJt7'

SOCIAL_AUTH_VK_OAUTH2_KEY = '6035656'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'Oe3O7aQiabVMnYbQFPa9'

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = 'f93fe2caad314e8086d535b63c906b0f'
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = '1e3e4233097f45ab9513ddbffec6f816'

SOCIAL_AUTH_MAILRU_OAUTH2_KEY = '754050'
SOCIAL_AUTH_MAILRU_OAUTH2_SECRET = 'ee92b0f6edb039891153744f3ee9ec4a'

SOCIAL_AUTH_FACEBOOK_KEY = '181297095728060'
SOCIAL_AUTH_FACEBOOK_SECRET = '627c4fc295bdc301df89d871eb68c9b4'
