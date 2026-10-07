# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from annoying.fields import AutoOneToOneField


class NoNotificationsTopic(models.Model):
    topic = AutoOneToOneField('pybb.Topic', on_delete=models.CASCADE, related_name='no_notifications')
    status = models.BooleanField(default=False)


class PostReply(models.Model):
    post = models.OneToOneField('pybb.Post', on_delete=models.CASCADE, related_name='reply_info')
    reply_to = models.ForeignKey('pybb.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_replies')

    class Meta:
        verbose_name = 'Ответ на сообщение'
        verbose_name_plural = 'Ответы на сообщения'

    def __str__(self):
        return 'Post #{} in reply to #{}'.format(self.post_id, self.reply_to_id if self.reply_to else None)


class ForumUserPreference(models.Model):
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_preferences')
    email_on_reply = models.BooleanField(
        default=True,
        verbose_name='Присылать email при ответе на мое сообщение или цитировании',
        help_text='Уведомлять по электронной почте, когда кто-то отвечает на ваше сообщение или цитирует его.'
    )

    class Meta:
        verbose_name = 'Настройки уведомлений форума'
        verbose_name_plural = 'Настройки уведомлений форума'

    def __str__(self):
        return 'Preferences for {}'.format(self.user.username)