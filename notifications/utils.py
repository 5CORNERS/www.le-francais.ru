from typing import List

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from notifications.models import Notification, NotificationUser


def blank_list(request):
	login_url = settings.LOGIN_URL + '?next=' + request.GET.get('path', '')
	if request.user.is_anonymous:
		return dict(authenticated=False, login_url=login_url)
	if Notification.objects.filter(
			datetime_creation__gte=request.user.date_joined).filter(
		Q(to_all=True)|Q(notificationuser__user=request.user),active=True).exclude(
		excpt=request.user).distinct().exists():
		has_notifications = True
	else:
		has_notifications = False
	return dict(
		authenticated=True,
		has_notifications=has_notifications,
		new_notifications=[],
		old_notifications=[],
		login_url=login_url
	)


def query_notifications(request):
	login_url = settings.LOGIN_URL + '?next=' + request.GET.get('path', '')
	user = request.user
	if user.is_anonymous:
		return dict(authenticated=False, login_url=login_url)
	notifications: List[Notification] = list(
		Notification.objects.select_related('image').filter(
			Q(to_all=True) | Q(notificationuser__user=user),
			active=True
		).exclude(datetime_creation__lt=user.date_joined).exclude(
			excpt=user).distinct().order_by(
			'-datetime_creation'))  # TODO: фильтровать по разрешениям
	if not notifications:
		has_notifications = False
	else:
		has_notifications = True
	notification_user_set = NotificationUser.objects.filter(
		user=user
	)
	notification_user_dict = {n.notification_id:n for n in notification_user_set}
	for notification in notifications:  # type: Notification
		notification_user = notification_user_dict.get(notification.pk, None)
		if notification_user is not None:
			if notification_user.is_viewed():
				notification._is_viewed[user.pk] = True
			if notification_user.is_visited():
				notification._is_visited[user.pk] = True
		else:
			notification._is_viewed[user.pk] = False
			notification._is_visited[user.pk] = False
	time_threshold = timezone.now() - timezone.timedelta(days=14)
	return dict(
		has_notifications=has_notifications,
		authenticated=True,
		old_notifications=[
			n.to_dict(user) for n in notifications if
			(n.datetime_creation > time_threshold or not n.is_viewed(user))],
		new_notifications=[
			n.to_dict(user) for n in notifications if not n.is_viewed(user)
		],
		login_url=login_url,
	)
