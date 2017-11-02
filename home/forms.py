from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _
from pybb.forms import EditProfileForm

from profiles.models import Profile
from custom_user.models import User


class CaptchaTestForm(forms.Form):
	captcha = CaptchaField()


class ChangeUsername(forms.ModelForm):
	username = forms.CharField(label=_('New username'))

	class Meta:
		model = User
		fields = ('username',)


class AuthenticationFormCaptcha(AuthenticationForm):
	captcha = CaptchaField(label=_('Captcha'))


class AORProfileForm(EditProfileForm):
	class Meta:
		model = Profile
		fields = ('autosubscribe', 'signature', 'show_signatures', 'time_zone',
		          'language', 'avatar',)

	signature = forms.CharField(widget=forms.Textarea, label=_('Signature'),
	                            required=False)
	# time_zone = forms.ChoiceField()


class SearchForm(forms.Form):
	q = forms.CharField()
