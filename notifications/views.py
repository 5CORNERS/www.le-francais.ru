from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from notifications.utils import query_notifications
from .models import Notification, NotificationUser


# def query_notifications(request):
#     login_url = settings.LOGIN_URL + '?next=' + request.GET.get('path', '')
#     if request.user.is_anonymous:
#         return dict(authenticated=False, login_url=login_url)
#     notifyes = list(
#         NotificationUser.objects.select_related('notification').filter(
#             user=request.user, notification__active=True).order_by(
#             '-notification__datetime_creation'))
#     if not notifyes:
#         has_notifyes = False
#     else:
#         has_notifyes = True
#     new_notifyes = list(filter(lambda x: x.check_datetime is None, notifyes))
#     old_notifyes = [x for x in notifyes if x not in new_notifyes]
#     return dict(
#         authenticated=True,
#         has_notifications=has_notifyes,
#         new_notifications=new_notifyes,
#         old_notifications=old_notifyes,
#         login_url=login_url,
#     )


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
    notifications = Notification.objects.prefetch_related('notificationuser_set').filter(Q(to_all=True) | Q(notificationuser__user=request.user),
            active=True).exclude(excpt=request.user).exclude(datetime_creation__lt=request.user.date_joined).distinct()
    new_notifyes = []
    for notify in notifications:  # type: Notification
        try:
            notification_user = notify.notificationuser_set.get(
                user=request.user)
            if notification_user.check_datetime is None:
                new_notifyes.append(notify)
        except NotificationUser.DoesNotExist:
            if notify.to_all:
                new_notifyes.append(notify)
    return HttpResponse(len(new_notifyes), status=200)


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
    notifyes = Notification.objects.prefetch_related('notificationuser_set').filter(pk__in=pks)
    for notify in notifyes:
        notification_user, created = notify.notificationuser_set.get_or_create(
            user=request.user
        )
    NotificationUser.objects.filter(notification_id__in=notifyes).update(check_datetime=timezone.now())
    return HttpResponse('OK', status=200)
