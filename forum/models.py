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


class PostReaction(models.Model):
    post = models.ForeignKey('pybb.Post', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_reactions')
    reaction_type = models.CharField(max_length=20, default='heart')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = 'Реакция на сообщение'
        verbose_name_plural = 'Реакции на сообщения'

    def __str__(self):
        return '{} by {} on Post #{}'.format(self.reaction_type, self.user.username, self.post_id)


class ForumAttachment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_attachments', verbose_name='Пользователь')
    post = models.ForeignKey('pybb.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_attachments', verbose_name='Сообщение')
    file = models.ImageField(upload_to='forum/images/%Y/%m/', verbose_name='Файл')
    filename = models.CharField(max_length=255, verbose_name='Исходное имя файла')
    file_size = models.PositiveIntegerField(verbose_name='Размер файла (байт)')
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name='Ширина')
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name='Высота')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Вложение форума'
        verbose_name_plural = 'Вложения форума'
        ordering = ['-created']

    def __str__(self):
        return '{} ({})'.format(self.filename, self.user.username if self.user else 'anonymous')


from django.db.models.signals import post_save
from django.dispatch import receiver
from pybb.models import Post
from forum.attachment_utils import link_attachments_to_post


@receiver(post_save, sender=Post)
def post_saved_link_attachments(sender, instance, **kwargs):
    link_attachments_to_post(instance, instance.body)

