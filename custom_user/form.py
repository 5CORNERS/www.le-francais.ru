from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationForm
from captcha.fields import CaptchaField

from .models import User


class MyCustomUserForm(RegistrationForm):
	email = forms.EmailField(
		help_text=_(u'email address'),
		required=True
	)
	username = forms.CharField(
		help_text=_(u'username'),
		required=True
	)
	captcha = CaptchaField()

	class Meta(UserCreationForm.Meta):
		fields = [
			User.EMAIL_FIELD,
			User.USERNAME_FIELD,
			'password1',
			'password2',
		]
		required_css_class = 'required'
