from django import forms
from snowpenguin.django.recaptcha3.fields import ReCaptchaField
from snowpenguin.django.recaptcha3.widgets import ReCaptchaHiddenInput

class CaptchaAllauthSignupForm(forms.Form):

    captcha = ReCaptchaField(widget=ReCaptchaHiddenInput, score_threshold=0.1)

    def signup(self, request, user):
        user.recaptcha3_score = self.cleaned_data['captcha'][1]
        user.save()
