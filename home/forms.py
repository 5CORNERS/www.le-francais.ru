from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _
from django_comments_xtd.forms import XtdCommentForm
from pybb.forms import EditProfileForm

from custom_user.models import User
from profiles.models import Profile

from django import forms
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from django_comments.forms import CommentForm

from django_comments_xtd.conf import settings
from django_comments_xtd.models import TmpXtdComment


class MyCommentForm(XtdCommentForm):
    followup = forms.BooleanField(required=False,
                                  label=_("Notify me about follow-up comments"))
    reply_to = forms.IntegerField(required=True, initial=0,
                                  widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        comment = kwargs.pop("comment", None)
        if comment:
            initial = kwargs.pop("initial", {})
            initial.update({"reply_to": comment.pk})
            kwargs["initial"] = initial
            followup_suffix = ('_%d' % comment.pk)
        else:
            followup_suffix = ''
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(
            label=_("Name"),
            widget=forms.TextInput(attrs={'placeholder': _('name'),
                                          'class': 'form-control'}))
        self.fields['email'] = forms.EmailField(
            label=_("Mail"), help_text=_("Required for comment verification"),
            widget=forms.TextInput(attrs={'placeholder': _('mail address'),
                                          'class': 'form-control'}))
        self.fields['url'] = forms.URLField(
            label=_("Link"), required=False,
            widget=forms.TextInput(attrs={
                'placeholder': _('url your name links to (optional)'),
                'class': 'form-control'}))
        self.fields['comment'] = forms.CharField(
            widget=forms.Textarea(attrs={'placeholder': _('Your comment'),
                                         'class': 'form-control'}),
            max_length=settings.COMMENT_MAX_LENGTH)
        self.fields['comment'].widget.attrs.pop('cols')
        self.fields['comment'].widget.attrs.pop('rows')
        self.fields['followup'].widget.attrs['id'] = (
            'id_followup%s' % followup_suffix)

    def get_comment_model(self):
        return TmpXtdComment

    def get_comment_create_data(self, site_id=None):
        data = super(CommentForm, self).get_comment_create_data(site_id=site_id)
        ctype = data.get('content_type')
        object_pk = data.get('object_pk')
        model = apps.get_model(ctype.app_label, ctype.model)
        target = model._default_manager.get(pk=object_pk)
        data.update({'thread_id': 0, 'level': 0, 'order': 1,
                     'parent_id': self.cleaned_data['reply_to'],
                     'followup': self.cleaned_data['followup'],
                     'content_object': target})
        return data


class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()


class ChangeUsername(forms.ModelForm):
    username = forms.CharField(label=_('New username'), strip=True)

    class Meta:
        model = User
        fields = ('username',)


class AuthenticationFormCaptcha(AuthenticationForm):
    captcha = CaptchaField(label=_('Captcha'))


class AORProfileForm(EditProfileForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'autosubscribe', 'signature', 'show_signatures', 'time_zone',
                  'language',)

    signature = forms.CharField(widget=forms.Textarea, label=_('Signature'),
                                required=False)
# time_zone = forms.ChoiceField()


class SearchForm(forms.Form):
    q = forms.CharField()
