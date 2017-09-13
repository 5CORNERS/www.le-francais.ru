from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.db.models import EmailField


class User(AbstractUser):
	email = EmailField(_('email address'), unique=True, error_messages={
		'unique': _("A user with that email adress already exists."),
	}, )
	USERNAME_FIELD = 'email'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
