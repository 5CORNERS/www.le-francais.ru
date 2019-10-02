import datetime
import json
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import SuspiciousOperation

from notifications.utils import query_notifications
from .models import Notification, NotificationUser, CheckNotifications


def notification_list_to_dict(notifications: list):
	return [notification.to_dict() for notification in notifications]


@require_GET
def get_notifications(request):
	user = request.user
	notifications = Notification.objects \
		.prefetch_related('image') \
		.order_by('datetime_creation') \
		.filter(notificationuser__user=user)
	data = {'notification_list': notification_list_to_dict(notifications)}
	return JsonResponse(data)


@require_GET
def get_new_notifications_count(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponse(0, status=200)
	new_notifications = Notification.objects.prefetch_related().filter(
		datetime_creation__gte=user.date_joined).filter(
		notificationuser__user=request.user,
		notificationuser__check_datetime__isnull=True, active=True
	)
	new_notifications_to_all = Notification.objects.prefetch_related().filter(
		to_all=True, datetime_creation__gte=user.date_joined).exclude(excpt=request.user).exclude(
		notificationuser__user=request.user)
	return HttpResponse(len(new_notifications)+ len(new_notifications_to_all), status=200)


@require_GET
def get_new_notifications(request):
	user = request.user
	notifications = Notification.objects \
		.order_by('datetime_creation') \
		.filter(notificationuser__user=user,
	            notificationuser__check_datetime=None)
	data = {'notification_list': notification_list_to_dict(notifications)}
	return JsonResponse(data)


@require_GET
def get_drop_content_html(request):
	data = query_notifications(request)
	return render(request, template_name='notifications/drop-content.html',
	              context=data)


@csrf_exempt
@require_POST
def has_new_notifications(request):
	user_check = request.user.check_notifications
	try:
		data:dict = json.loads(request.body)
		if user_check.has_new_notifications or user_check.last_update > timezone.datetime.utcfromtimestamp(data['datetime']/1000).replace(tzinfo=datetime.timezone.utc):
			return JsonResponse({'hasNewNotifications': True})
	except ValueError:
		raise SuspiciousOperation('Invalid JSON')
	except KeyError:
		raise SuspiciousOperation('Invalid JSON')
	return JsonResponse({'hasNewNotifications': False}, status=200)
@require_GET
def check_notification(request, pk):
	user = request.user
	NotificationUser.objects.get(notification_id=pk,
	                             user=user).check_as_viewed()
	return redirect('notifications:get')


@csrf_exempt
@require_POST
def check_notifications(request):
	pks = list(map(int, request.POST.get('pks', '').split(',')))
	notifyes = Notification.objects.prefetch_related(
		'notificationuser_set').filter(pk__in=pks)
	for notify in notifyes:
		notification_user, created = notify.notificationuser_set.get_or_create(
			user=request.user
		)
	NotificationUser.objects.filter(notification_id__in=notifyes).update(
		check_datetime=timezone.now())
	return HttpResponse('OK', status=200)
