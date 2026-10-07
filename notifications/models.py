# -*- coding: utf-8 -*-
import ast
import json
import uuid
from datetime import datetime

import requests
from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.baseconv import base64
from postman.models import Message

from custom_user.models import User
from pybb.models import Post, Like, Topic, Profile
from django.contrib.sites.models import Site
from pybb import util as pybb_util
from pybb.permissions import perms as pybb_perms

from le_francais_dictionary.models import UserDayRepetition, \
	UserWordRepetition, get_repetition_words_query
from . import consts


# Create your models here.

class NotificationImage(models.Model):
	url = models.URLField(null=False, blank=False)
	base64 = models.BinaryField(null=True, default=None)

	# def save(self, *args, **kwargs):
	# 	if self.base64 is None:
	# 		self.base64 = base64.b64encode(requests.get(self.url).content)
	# 	super(NotificationImage, self).save(*args, **kwargs)

class Notification(models.Model):
	MODERATION = 'MD'
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

	def __init__(self, *args, **kwargs):
		super(Notification, self).__init__(*args, **kwargs)
		self._is_viewed = {}
		self._is_visited = {}
		self._view_datetimes = {}
		self._visit_datetimes = {}

	def is_visited(self, user):
		if not user.pk in self._is_visited.keys():
			notification_user = self.notificationuser_set.filter(
				user=user
			)
			if notification_user.exists() and notification_user.first().is_visited():
				self._is_visited[user.pk] = True
			else:
				self._is_visited[user.pk] = False
		return self._is_visited[user.pk]

	def is_viewed(self, user):
		if not user.pk in self._is_viewed.keys():
			notification_user = self.notificationuser_set.filter(
				user=user
			)
			if notification_user.exists() and notification_user.first().is_viewed():
				self._is_viewed[user.pk] = True
			else:
				self._is_viewed[user.pk] = False
		return self._is_viewed[user.pk]

	def get_view_datetime(self, user):
		if not user.pk in self._view_datetimes.keys():
			notification_user = self.notificationuser_set.filter(
				user=user
			)
			if notification_user.exists():
				self._view_datetimes[user.pk] = notification_user.first().check_datetime
			else:
				self._view_datetimes[user.pk] = None
		return self._view_datetimes[user.pk]

	def get_visit_datetime(self, user):
		if not user.pk in self._visit_datetimes.keys():
			notification_user = self.notificationuser_set.filter(
				user=user
			)
			if notification_user.exists():
				self._visit_datetimes[user.pk] = notification_user.first().visit_datetime
			else:
				self._visit_datetimes[user.pk] = None
		return self._visit_datetimes[user.pk]

	# TODO check this
	@property
	def text(self):
		try:
			return getattr(consts, self.category + '_TEXT', '').format(
				**self.data)
		except TypeError:
			self.data = ast.literal_eval(self.data)
			return self.text

	def get_html(self):
		return render_to_string(
			f'notifications/notifications_templates/{self.category}.html',
			context=dict(**self.data, self=self)
		)

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

	def to_push_json(self):
		data = dict(
			Title=self.title,
			Text=self.text,
			ClickUrl=self.get_click_url(),
			ImageBase64=self.image.base64,
			pk=self.pk,
		)
		return json.loads(data)

	def to_dict(self, user, add_self=True):
		data = dict(
			self=self,
			is_visited=self.is_visited(user),
			is_viewed=self.is_viewed(user),
			visit_datetime=self.get_visit_datetime(user),
			view_datetime=self.get_view_datetime(user),
			image_url=self.image.url,
			url=self.get_click_url(),
			html=self.get_html(),
			datetime=self.datetime_creation,
			pk=self.pk,
		)
		if not add_self:
			data.pop('self')
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

	def is_visited(self):
		if self.visit_datetime is not None:
			return True
		return False

	def is_viewed(self):
		if self.check_datetime is not None:
			return True
		return False


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
	if not result.strip():
		for line in post.splitlines():
			cleaned = line.lstrip('> ').strip()
			if cleaned:
				result += cleaned + ' '
	limit = 50
	tail = len(result) > limit and '...' or ''
	return result[:50] + tail


def create_moderator_notification(sender, instance):
	if not isinstance(instance, Post):
		return
	notification = Notification(
		title='Пост требует модерации',
		category=Notification.MODERATION,
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
	perm = Permission.objects.get(codename='change_post')
	users_to_notify = User.objects.filter(
		Q(is_superuser=True) | Q(groups__permissions=perm) | Q(user_permissions=perm)
	).distinct()
	for user in users_to_notify:
		try:
			notification_user, created = NotificationUser.objects.get_or_create(
				notification=notification,
				user=user
			)
		except NotificationUser.MultipleObjectsReturned:
			NotificationUser.objects.filter(
				notification=notification, user=user
			)[1:].delete()

def create_pybb_post_notification(sender, instance: Post, **kwargs):
	if not instance.on_moderation and instance.updated is None:
		from forum.models import PostReply
		from forum.utils import get_mentioned_and_quoted_users, send_forum_mail

		# 1. Process reply_to if passed
		reply_to_id = getattr(instance, '_reply_to_id', None)
		if reply_to_id:
			try:
				PostReply.objects.get_or_create(post=instance, defaults={'reply_to_id': reply_to_id})
			except Exception:
				pass

		direct_reply_user = None
		if hasattr(instance, 'reply_info') and instance.reply_info.reply_to:
			target_post = instance.reply_info.reply_to
			if target_post.user and target_post.user.pk != instance.user.pk:
				direct_reply_user = target_post.user

		# 2. Extract quoted and mentioned users from body
		excluded_ids = [instance.user.pk]
		if direct_reply_user:
			excluded_ids.append(direct_reply_user.pk)
		quoted_users = get_mentioned_and_quoted_users(instance.body, exclude_user_ids=excluded_ids)
		for u in quoted_users:
			excluded_ids.append(u.pk)

		# 3. Topic subscribers
		subscribers = list(instance.topic.subscribers.exclude(id__in=excluded_ids))

		# 4. In-app bell notifications
		avatar_image = NotificationImage.objects.get_or_create(
			url=instance.user.pybb_profile.avatar_url
		)[0]

		# 4a. Notification for direct reply
		if direct_reply_user:
			notif_reply = Notification.objects.create(
				title='Ответ на ваше сообщение',
				category=Notification.REPLYES,
				data=dict(
					username=str(instance.user),
					post_name=clean_post(instance.body),
					post_url=instance.get_absolute_url(),
					topic_name=str(instance.topic),
					topic_url=instance.topic.get_absolute_url(),
					is_reply_to_you=True,
				),
				click_url=instance.get_absolute_url(),
				image=avatar_image,
				content_object=instance,
			)
			NotificationUser.objects.create(notification=notif_reply, user=direct_reply_user)

		# 4b. Notification for quoted/mentioned users
		if quoted_users:
			notif_quote = Notification.objects.create(
				title='Вас упомянули в теме',
				category=Notification.REPLYES,
				data=dict(
					username=str(instance.user),
					post_name=clean_post(instance.body),
					post_url=instance.get_absolute_url(),
					topic_name=str(instance.topic),
					topic_url=instance.topic.get_absolute_url(),
					is_quote=True,
				),
				click_url=instance.get_absolute_url(),
				image=avatar_image,
				content_object=instance,
			)
			for u in quoted_users:
				NotificationUser.objects.create(notification=notif_quote, user=u)

		# 4c. Notification for thread subscribers
		if subscribers:
			notif_sub = Notification.objects.create(
				title='Новый ответ в теме',
				category=Notification.REPLYES,
				data=dict(
					username=str(instance.user),
					post_name=clean_post(instance.body),
					post_url=instance.get_absolute_url(),
					topic_name=str(instance.topic),
					topic_url=instance.topic.get_absolute_url(),
				),
				click_url=instance.get_absolute_url(),
				image=avatar_image,
				content_object=instance,
			)
			for u in subscribers:
				NotificationUser.objects.create(notification=notif_sub, user=u)

		# 5. Send emails
		current_site = Site.objects.get_current()
		delete_url = reverse('pybb:delete_subscription', args=[instance.topic.id])
		email_context = {
			'post': instance,
			'post_url': 'http://%s%s' % (current_site, instance.get_absolute_url()),
			'topic_url': 'http://%s%s' % (current_site, instance.topic.get_absolute_url()),
			'delete_url_full': 'http://%s%s' % (current_site, delete_url),
			'site': current_site,
		}

		if direct_reply_user:
			send_forum_mail([direct_reply_user], 'reply_email', email_context, preference_type='reply')
		if quoted_users:
			send_forum_mail(quoted_users, 'quote_email', email_context, preference_type='reply')
		if subscribers:
			send_forum_mail(subscribers, 'subscription_email', email_context, preference_type='subscription')

		# 6. Auto-subscribe post author if requested
		if pybb_util.get_pybb_profile(instance.user).autosubscribe and \
				pybb_perms.may_subscribe_topic(instance.user, instance.topic):
			instance.topic.subscribers.add(instance.user)

	elif instance.on_moderation:
		if instance.updated is not None:
			Post.objects.filter(id=instance.id).update(updated=None)
		else:
			create_moderator_notification(sender, instance)
	# hide topic notification if topic is on moderation and show if it was confirmed
	if instance.is_topic_head:
		topic_notification = Notification.objects.filter(
			content_type=ContentType.objects.get_for_model(Topic),
			object_id=instance.topic.pk
		)
		if instance.on_moderation:
			topic_notification.update(active=False)
		else:
			topic_notification.update(active=True)

def create_pybb_like_notification(sender, instance: Like, **kwargs):
	if instance.post.user == instance.profile.user:
		return
	from forum.models import PostReaction
	if PostReaction.objects.filter(post_id=instance.post_id, user_id=instance.profile.user_id).exists():
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


def create_post_reaction_notification(sender, instance, **kwargs):
	if instance.post.user == instance.user:
		return
	from forum.reactions import get_reaction
	reaction_info = get_reaction(instance.reaction_type)
	reaction_label = reaction_info['label'] if reaction_info else 'Реакция'
	reaction_emoji = reaction_info['emoji'] if reaction_info else None
	reaction_image = reaction_info['image'] if reaction_info else None

	try:
		notification, created = Notification.objects.get_or_create(
			content_type=ContentType.objects.get_for_model(instance.__class__),
			object_id=instance.id,
			image=NotificationImage.objects.get_or_create(
				url=instance.user.pybb_profile.avatar_url
			)[0],
		)
	except Notification.MultipleObjectsReturned:
		for notification in Notification.objects.filter(
				content_type=ContentType.objects.get_for_model(instance.__class__),
				object_id=instance.id,
		)[1:]:
			notification.delete()
		return create_post_reaction_notification(sender, instance, **kwargs)

	notification.title = 'Новая реакция на ваш пост: {}'.format(reaction_label)
	notification.category = notification.LIKES
	notification.data = dict(
		username=instance.user.pybb_profile.get_display_name(),
		post_url=instance.post.get_absolute_url(),
		post_name=clean_post(instance.post.body),
		topic_url=instance.post.topic.get_absolute_url(),
		topic_name=str(instance.post.topic),
		reaction_type=instance.reaction_type,
		reaction_label=reaction_label,
		reaction_emoji=reaction_emoji,
		reaction_image=reaction_image,
	)
	notification.click_url = instance.post.get_absolute_url()
	notification.image = NotificationImage.objects.get_or_create(
		url=instance.user.pybb_profile.avatar_url
	)[0]
	notification.active = instance.active
	notification.save()

	if created:
		NotificationUser.objects.create(
			notification=notification,
			user=instance.post.user,
		)


def delete_post_reaction_notification(sender, instance, **kwargs):
	Notification.objects.prefetch_related('notificationuser_set') \
		.filter(content_type=ContentType.objects.get_for_model(instance.__class__),
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


def delete_pybb_notification(sender, instance: Topic, **kwargs):
	Notification.objects.filter(
		content_type=ContentType.objects.get_for_model(sender),
		object_id=instance.pk,
	).update(active=False)


post_save.connect(create_pybb_post_notification, Post)
post_delete.connect(delete_pybb_notification, Post)
post_save.connect(create_pybb_like_notification, Like)
post_delete.connect(delete_pybb_like_notification, Like)
from forum.models import PostReaction
post_save.connect(create_post_reaction_notification, PostReaction)
post_delete.connect(delete_post_reaction_notification, PostReaction)

post_save.connect(create_postman_notification, Message)
post_save.connect(create_pybb_topic_notification, Topic)
post_delete.connect(delete_pybb_notification, Topic)

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
	try:
		NotificationUser.objects.get_or_create(
			notification=notification,
			user=instance.user
		)
	except NotificationUser.MultipleObjectsReturned:
		NotificationUser.objects.filter(
			notification=notification,
			user=instance.user
		)[1:].delete()
