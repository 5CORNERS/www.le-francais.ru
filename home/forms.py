from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _
from django_comments_xtd.forms import XtdCommentForm
from pybb.forms import EditProfileForm, PostForm

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


class AorPostForm(PostForm):
    reply_to_post = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AorPostForm, self).__init__(*args, **kwargs)
        self.use_required_attribute = False
        if 'reply_to_post' in self.initial:
            self.fields['reply_to_post'].initial = self.initial['reply_to_post']
        if 'body' in self.fields:
            self.fields['body'].widget = forms.Textarea(attrs={
                'class': 'form-control forum-markdown-textarea',
                'rows': '10',
            })
            self.fields['body'].widget.attrs.pop('required', None)


    def save(self, commit=True):
        post, topic = super(AorPostForm, self).save(commit=commit)
        reply_to_id = self.cleaned_data.get('reply_to_post')
        if reply_to_id:
            post._reply_to_id = reply_to_id
            if commit and post.pk:
                from forum.models import PostReply
                try:
                    PostReply.objects.get_or_create(post=post, defaults={'reply_to_id': reply_to_id})
                except Exception:
                    pass
        if commit and post and post.pk:
            from forum.attachment_utils import link_attachments_to_post
            try:
                link_attachments_to_post(post, post.body)
            except Exception:
                pass
        return post, topic



class AORProfileForm(EditProfileForm):
    email_on_reply = forms.BooleanField(
        required=False,
        label=_('Присылать email при ответе на мое сообщение или цитировании'),
        help_text=_('Уведомлять по электронной почте, когда кто-то отвечает на ваше сообщение или цитирует его.')
    )

    signature = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label=_('Подпись'),
        required=False
    )

    class Meta:
        model = Profile
        fields = (
            'avatar',
            'autosubscribe',
            'receive_emails',
            'email_on_reply',
            'signature',
            'show_signatures',
            'time_zone',
            'language',
        )

    def __init__(self, *args, **kwargs):
        super(AORProfileForm, self).__init__(*args, **kwargs)
        if 'autosubscribe' in self.fields:
            self.fields['autosubscribe'].label = _('Автоматически подписываться на темы, где я пишу')
        if 'receive_emails' in self.fields:
            self.fields['receive_emails'].label = _('Присылать email о новых ответах во всех отслеживаемых темах')
            self.fields['receive_emails'].help_text = _('Отключите, если не хотите получать письма о каждом новом сообщении в подписанных темах.')
        if 'show_signatures' in self.fields:
            self.fields['show_signatures'].label = _('Показывать подписи других пользователей')

        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            prefs = getattr(self.instance.user, 'forum_preferences', None)
            if prefs is not None:
                self.fields['email_on_reply'].initial = prefs.email_on_reply
            else:
                self.fields['email_on_reply'].initial = True

    def save(self, commit=True):
        profile = super(AORProfileForm, self).save(commit=commit)
        if hasattr(profile, 'user') and profile.user:
            from forum.models import ForumUserPreference
            pref, _ = ForumUserPreference.objects.get_or_create(user=profile.user)
            pref.email_on_reply = self.cleaned_data.get('email_on_reply', True)
            pref.save()
        return profile


class SearchForm(forms.Form):
    q = forms.CharField()
