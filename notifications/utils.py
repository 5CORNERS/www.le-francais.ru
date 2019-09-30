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
	if request.user.is_anonymous:
		return dict(authenticated=False, login_url=login_url)
	notifications: List[Notification] = list(
		Notification.objects.prefetch_related('notificationuser_set',
		                                      'image').filter(
			Q(to_all=True) | Q(notificationuser__user=request.user),
			active=True
		).exclude(datetime_creation__lt=request.user.date_joined).exclude(
			excpt=request.user).distinct().order_by(
			'-datetime_creation'))  # TODO: фильтровать по разрешениям
	if not notifications:
		has_notifications = False
	else:
		has_notifications = True
	new_notifications: List[Notification] = []
	for notify in notifications:  # type: Notification
		try:
			notification_user = notify.notificationuser_set.get(
				user=request.user)
			if notification_user.check_datetime is None:
				new_notifications.append(notify)
		except NotificationUser.DoesNotExist:
			if notify.to_all:
				new_notifications.append(notify)
		except NotificationUser.MultipleObjectsReturned:
			first_notify = notify.notificationuser_set.filter(
				user=request.user)[:1].values_list("id", flat=True)
			notify.notificationuser_set.exclude(
				pk__in=list(first_notify)).delete()
			query_notifications(request)
	time_threshold = timezone.now() - timezone.timedelta(days=14)
	old_notifications: List[Notification] = [x for x in notifications if
	                                         x not in new_notifications and x.datetime_creation > time_threshold]
	return dict(
		authenticated=True,
		has_notifications=has_notifications,
		new_notifications=new_notifications,
		old_notifications=old_notifications,
		login_url=login_url,
	)
