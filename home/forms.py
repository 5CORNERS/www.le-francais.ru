from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import ugettext as _
from pybb.forms import EditProfileForm
from registration.forms import RegistrationFormUniqueEmail
from profiles.models import Profile
from captcha.fields import CaptchaField

class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()


class RegistrationFormCaptcha(RegistrationFormUniqueEmail):
    captcha = CaptchaField(label=_('Captcha'))


class AuthenticationFormCaptcha(AuthenticationForm):
    captcha = CaptchaField(label=_('Captcha'))


class AORProfileForm(EditProfileForm):
    class Meta:
        model = Profile
        fields = ('signature', 'date_show_type', 'show_signatures', 'time_zone',
                  'language', 'avatar', 'icq', 'skype', 'jabber', 'site', 'interests')

    signature = forms.CharField(widget=forms.Textarea, label=_('Signature'),
        required=False)


class SearchForm(forms.Form):
    q = forms.CharField()
