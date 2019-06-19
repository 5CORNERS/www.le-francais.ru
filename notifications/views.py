from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import Notification, NotificationUser


# Create your views here.


def notification_list_to_json(notifications: list):
    return [notification.to_json() for notification in notifications]


@require_POST
def get_notifications(request):
    user = request.user
    notifications = Notification.objects \
        .order_by('datetime_creation') \
        .filter(notificationuser=user)
    data = {'notification_list': notification_list_to_json(notifications)}
    return JsonResponse(data)


@require_GET
def check_notification(request, pk):
    user = request.user
    NotificationUser.objects.get(notification_id=pk,
                                 user=user).check_as_viewed()
    return redirect('notifications:get')


@csrf_exempt
@require_POST
def check_notifications(request):
    user = request.user
    pks = list(map(int, request.POST.get('pks', '').split(',')))
    NotificationUser.objects.filter(user=user, pk__in=pks).update(
        check_datetime=timezone.now())
    return HttpResponse('OK', status=200)
