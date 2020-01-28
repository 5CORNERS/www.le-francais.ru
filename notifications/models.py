# -*- coding: utf-8 -*-
import ast
import json
import uuid
from datetime import datetime

from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.urls import reverse
from django.utils import timezone
from postman.models import Message

from custom_user.models import User
from pybb.models import Post, Like, Topic, Profile
from pybb.models import Post, Like

from le_francais_dictionary.models import UserDayRepetition, \
	UserWordRepetition, get_repetition_words_query
from . import consts


# Create your models here.

class NotificationImage(models.Model):
	url = models.URLField()
	base64 = models.BinaryField(null=True, default=None)


class Notification(models.Model):
	LIKES = 'LK'
	REPLYES = 'RP'
	MESSAGES = 'MG'
	TOPICS = 'TP'
	INTERVAL_REPETITIONS = 'IR'
	CATEGORIES_CHOICES = [
		(LIKES, 'Likes'),
		(REPLYES, 'Replies'),
		(MESSAGES, 'Messages'),
		(TOPICS, 'Topics'),
		(INTERVAL_REPETITIONS, 'Interval Repetitions')
	]
	title = models.CharField(max_length=50)
	key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	# field was removed
	# text = models.CharField(max_length=100)
	click_url = models.URLField()
	image = models.ForeignKey('NotificationImage', on_delete=models.PROTECT)
	text_1st_bt = models.CharField(max_length=34, null=True, default=None)
	text_2nd_bt = models.CharField(max_length=34, null=True, default=None)
	url_1st_bt = models.URLField(null=True, default=None)
	url_2nd_bt = models.URLField(null=True, default=None)
	datetime_creation = models.DateTimeField(auto_now_add=True)

	data = JSONField(null=True)
	category = models.CharField(choices=CATEGORIES_CHOICES, max_length=10,
	                            null=True)

	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	active = models.BooleanField(default=True)

	to_all = models.BooleanField(default=False)
	excpt = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
	push_time = models.DateTimeField(null=True)

	# TODO check this
	@property
	def text(self):
		try:
			return getattr(consts, self.category + '_TEXT', '').format(
				**self.data)
		except TypeError:
			self.data = ast.literal_eval(self.data)
			return self.text

	def get_click_url(self):
		return reverse('notifications:view', args=[self.key])

	def get_1st_btn_url(self):
		return self.get_click_url() + '?button=1'

	def get_2nd_btn_url(self):
		return self.get_click_url() + '?button=2'

	def check_datetime(self, user):
		try:
			return self.notificationuser_set.get(user=user).check_datetime
		except NotificationUser.DoesNotExist:
			return None

	def to_json(self):
		data = dict(
			Title=self.title,
			Text=self.text,
			ClickUrl=self.get_click_url(),
			ImageBase64=self.image.base64,
			pk=self.pk,
		)
		return json.loads(data)

	def to_dict(self):
		data = dict(
			image=self.image.url,
			html=self.text,
			url=self.get_click_url(),
			datetime=self.datetime_creation,
			pk=self.pk,
		)
		return data


class CheckNotifications(models.Model):
	user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True,
	                         on_delete=models.CASCADE,
	                         related_name='check_notifications')
	has_new_notifications = models.BooleanField(default=True)
	last_update = models.DateTimeField(auto_now=True)

	def set(self, arg):
		self.has_new_notifications = arg
		self.save()
		return self

	def __bool__(self):
		return self.has_new_notifications


class NotificationUser(models.Model):
	notification = models.ForeignKey('Notification', on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	check_datetime = models.DateTimeField(null=True, default=None)
	visit_datetime = models.DateTimeField(null=True, default=None)

	success = models.NullBooleanField(null=True, default=None)
	error_description = models.CharField(max_length=300, null=True,
	                                     default=None)
	remote_id = models.CharField(max_length=16, null=True, default=None)
	status = models.CharField(max_length=16, null=True, default=None)

	def check_as_viewed(self):
		if not self.check_datetime:
			self.check_datetime = timezone.now()
			self.save()

	def check_as_visited(self):
		if not self.visit_datetime:
			self.visit_datetime = timezone.now()
			self.save()


def check_users(sender, instance, **kwargs):
	if isinstance(instance, Notification) and instance.to_all:
		CheckNotifications.objects.all().exclude(user=instance.excpt).update(
			has_new_notifications=True)
	elif isinstance(instance, NotificationUser):
		instance.user.check_notifications.has_new_notifications = True
		instance.user.check_notifications.save()


def clean_post(post: str) -> str:
	result = ''
	for line in post.splitlines():
		if not line.startswith('>') and not line == '':
			result += line + ' '
	limit = 50
	tail = len(result) > limit and '...' or ''
	return result[:50] + tail


def create_pybb_post_notification(sender, instance: Post, **kwargs):
	if instance.updated is None:
		notification = Notification(
			title='Новый ответ в теме',
			category=Notification.REPLYES,
			data=dict(
				username=str(instance.user),
				post_name=clean_post(instance.body),
				post_url=instance.get_absolute_url(),
				topic_name=str(instance.topic),
				topic_url=instance.topic.get_absolute_url()
			),
			click_url=instance.get_absolute_url(),
			image=NotificationImage.objects.get_or_create(
				url=instance.user.pybb_profile.avatar_url
			)[0],
			content_object=instance,
		)
		notification.save()
		users_to_notify = User.objects.filter(
			id__in=instance.topic.subscribers.all()).exclude(
			id=instance.user.id)
		for user in users_to_notify:
			notification_user, created = NotificationUser.objects.get_or_create(
				notification=notification,
				user=user
			)


def create_pybb_like_notification(sender, instance: Like, **kwargs):
	if instance.post.user == instance.profile.user:
		return
	try:
		notification, created = Notification.objects.get_or_create(
			content_type=ContentType.objects.get_for_model(Like),
			object_id=instance.id,
			image=NotificationImage.objects.get_or_create(
				url=instance.profile.avatar_url
			)[0],
		)
	except Notification.MultipleObjectsReturned:
		for notification in Notification.objects.filter(
				content_type=ContentType.objects.get_for_model(Like),
				object_id=instance.id,
		)[1:]:
			notification.delete()
		return create_pybb_like_notification(sender, instance, **kwargs)
	if created:
		notification.title = 'Ваш пост отметили как понравившийся'
		notification.category = notification.LIKES
		notification.data = dict(username=instance.profile.get_display_name(),
		                         post_url=instance.post.get_absolute_url(),
		                         post_name=clean_post(instance.post.body),
		                         topic_url=instance.post.topic.get_absolute_url(),
		                         topic_name=str(instance.post.topic))
		notification.click_url = instance.post.get_absolute_url()
		notification.image = NotificationImage.objects.get_or_create(
			url=instance.profile.avatar_url
		)[0]
		NotificationUser.objects.create(
			notification=notification,
			user=instance.post.user,
		)
	else:
		notification.active = True
	notification.save()


def delete_pybb_like_notification(sender, instance: Like, **kwargs):
	Notification.objects.prefetch_related('notificationuser_set') \
		.filter(content_type=ContentType.objects.get_for_model(Like),
	            object_id=instance.id) \
		.update(active=False)


def create_postman_notification(sender, instance: Message, **kwargs):
	if kwargs['created']:
		data = dict(
			sender=str(instance.sender),
			message=instance.body[:20] + '...' if len(
				instance.body) > 20 else instance.body,
			message_url=instance.get_absolute_url(),
		)
		notification, created = Notification.objects.get_or_create(
			category=Notification.MESSAGES,
			data=data,
			click_url=data['message_url'],
			image=NotificationImage.objects.get_or_create(
				url=instance.sender.pybb_profile.avatar_url
			)[0],
			content_type=ContentType.objects.get_for_model(sender),
			object_id=instance.pk,
		)
		NotificationUser.objects.create(
			notification=notification,
			user=instance.recipient
		)


def create_pybb_topic_notification(sender, instance: Topic, **kwargs):
	if not kwargs['created']:
		return
	data = dict(
		author=str(instance.user),
		name=instance.name[:40] + '...' if len(
			instance.name) > 40 else instance.name,
		topic_url=instance.get_absolute_url(),
	)
	notification, created = Notification.objects.get_or_create(
		category=Notification.TOPICS,
		data=data,
		click_url=data['topic_url'],
		image=NotificationImage.objects.get_or_create(
			url=instance.user.pybb_profile.avatar_url
		)[0],
		content_type=ContentType.objects.get_for_model(sender),
		object_id=instance.pk,
		to_all=True,
		excpt=instance.user,
	)


def delete_pybb_topic_notification(sender, instance: Topic, **kwargs):
	Notification.objects.filter(
		content_type=ContentType.objects.get_for_model(sender),
		object_id=instance.pk,
	).update(active=False)


post_save.connect(create_pybb_post_notification, Post)
post_save.connect(create_pybb_like_notification, Like)
post_delete.connect(delete_pybb_like_notification, Like)
post_save.connect(create_postman_notification, Message)
post_save.connect(create_pybb_topic_notification, Topic)
post_delete.connect(delete_pybb_topic_notification, Topic)

post_save.connect(check_users, NotificationUser)
post_save.connect(check_users, Notification)


def create_dictionary_notification(sender, instance: UserDayRepetition, **kwargs):
	try:
		site_forum_profile = Profile.objects.get(pk=727).avatar_url
		image_url = Profile.objects.get(pk=727).avatar_url
	except Profile.DoesNotExist:
		image_url = 'https://www.le-francais.ru/static/images/cat_logo.png'
	from le_francais_dictionary.utils import message
	all_repetitions_count = get_repetition_words_query(instance.user).count()
	if all_repetitions_count != len(instance.repetitions):
		all_message = f' (всего их {all_repetitions_count})'
	else:
		all_message = ''
	notification, created = Notification.objects.get_or_create(
		image=NotificationImage.objects.get_or_create(
			url=image_url
		)[0],
		title='Доступны новые слова для повторения',
		category=Notification.INTERVAL_REPETITIONS,
		data=dict(
			url=reverse('dictionary:app_repeat'),
			quantity_message=message(len(instance.repetitions)),
			all=all_message
		),
		click_url=reverse('dictionary:app_repeat'),
		content_type=ContentType.objects.get_for_model(UserDayRepetition),
		object_id=instance.pk
	)
	if created:
		print(f'Created Notification {notification.datetime_creation} -- {len(instance.repetitions)}')
	NotificationUser.objects.get_or_create(
		notification=notification,
		user=instance.user
	)
