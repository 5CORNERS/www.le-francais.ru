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


def extract_usernames_from_text(text):
    if not text:
        return set()
    # 1. Quoted authors: > **Username**:
    quoted = re.findall(r'>\s*\*\*([^\*\n\r]+?)\*\*:', text)
    # 2. Addressed authors at line start: **Username**,
    addressed = re.findall(r'(?:^|\n)\s*\*\*([^\*\n\r]+?)\*\*,', text)
    # 3. Direct @mentions: @Username
    mentions = re.findall(r'(?<![\w@])@([a-zA-Z0-9_.@+-]+)', text)

    all_names = set()
    for name in quoted + addressed + mentions:
        cleaned = name.strip()
        if cleaned:
            all_names.add(cleaned)
    return all_names


def get_mentioned_and_quoted_users(text, exclude_user_ids=None):
    if not text:
        return []
    names = extract_usernames_from_text(text)
    if not names:
        return []

    User = get_user_model()
    qs = User.objects.filter(username__in=names)
    if exclude_user_ids:
        qs = qs.exclude(id__in=exclude_user_ids)
    return list(qs)


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

    old_lang = translation.get_language()
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
        translation.activate(lang)

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

    translation.activate(old_lang)
