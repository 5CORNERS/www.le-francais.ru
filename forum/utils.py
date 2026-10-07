# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.validators import validate_email
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import translation
from pybb import compat, util
from pybb.compat import send_mass_html_mail

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def extract_quoted_and_mentioned_names(text):
    if not text:
        return set(), set()
    # 1. Quoted authors: > **Username**:
    quoted_raw = re.findall(r'>\s*\*\*([^\*\n\r]+?)\*\*:', text)
    quoted = set(name.strip() for name in quoted_raw if name.strip())

    # 2. Addressed authors at line start: **Username**,
    addressed = re.findall(r'(?:^|\n)\s*\*\*([^\*\n\r]+?)\*\*,', text)
    # 3. Direct @mentions: @Username
    mentions = re.findall(r'(?<![\w@])@([a-zA-Z0-9_.\u0400-\u04FF@+-]+)', text)

    mentioned = set(name.strip().rstrip('.,:;!?') for name in (addressed + mentions) if name.strip().rstrip('.,:;!?'))
    # Users who were quoted do not need a duplicate mention notification
    mentioned = mentioned - quoted
    return quoted, mentioned


def extract_usernames_from_text(text):
    quoted, mentioned = extract_quoted_and_mentioned_names(text)
    return quoted | mentioned


def get_quoted_and_mentioned_users(text, exclude_user_ids=None):
    if not text:
        return [], []
    quoted_names, mentioned_names = extract_quoted_and_mentioned_names(text)
    User = get_user_model()
    quoted_users = list(User.objects.filter(username__in=quoted_names)) if quoted_names else []
    mentioned_users = list(User.objects.filter(username__in=mentioned_names)) if mentioned_names else []
    if exclude_user_ids:
        quoted_users = [u for u in quoted_users if u.id not in exclude_user_ids]
        mentioned_users = [u for u in mentioned_users if u.id not in exclude_user_ids]
    return quoted_users, mentioned_users


def get_mentioned_and_quoted_users(text, exclude_user_ids=None):
    quoted, mentioned = get_quoted_and_mentioned_users(text, exclude_user_ids=exclude_user_ids)
    return quoted + mentioned


def send_forum_mail(users, template, context=None, preference_type='reply'):
    """
    Sends customized forum notification emails.
    preference_type:
      - 'reply': checks user.forum_preferences.email_on_reply (default True)
      - 'subscription': checks user.pybb_profile.receive_emails (default True)
    """
    if not users:
        return

    context = dict(context or {})
    current_site = context.get('site') or Site.objects.get_current()
    context['site'] = current_site
    if 'profile_settings_url' not in context:
        context['profile_settings_url'] = 'http://%s%s' % (
            current_site, reverse('pybb:edit_profile')
        )

    from_email = getattr(settings, 'PYBB_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', None))

    mails = []
    for user in users:
        if preference_type == 'reply':
            # Check user.forum_preferences.email_on_reply
            prefs = getattr(user, 'forum_preferences', None)
            if prefs is not None and not prefs.email_on_reply:
                continue
        elif preference_type == 'subscription':
            profile = util.get_pybb_profile(user)
            if not getattr(profile, 'receive_emails', True):
                continue

        try:
            validate_email(user.email)
        except Exception:
            continue

        if user.email == '%s@example.com' % getattr(user, compat.get_username_field()):
            continue

        user_context = dict(context)
        user_context['user'] = user

        profile = util.get_pybb_profile(user)
        lang = getattr(profile, 'language', None) or settings.LANGUAGE_CODE
        with translation.override(lang):
            subject = render_to_string('pybb/mail_templates/%s_subject.html' % template, user_context)
            subject = ''.join(subject.splitlines())
            user_context['subject'] = subject

            txt_message = render_to_string('pybb/mail_templates/%s_body.html' % template, user_context)

            headers = {}
            if 'delete_url_full' in user_context:
                headers['List-Unsubscribe'] = '<%s>' % user_context['delete_url_full']

            try:
                html_message = render_to_string('pybb/mail_templates/%s_body-html.html' % template, user_context)
            except TemplateDoesNotExist:
                mails.append((subject, txt_message, from_email, [user.email], None, headers))
            else:
                mails.append((subject, txt_message, from_email, [user.email], html_message, headers))

    if mails:
        send_mass_html_mail(mails, fail_silently=True)
