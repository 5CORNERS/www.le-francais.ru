from typing import List

from django.conf import settings
from django.db.models import Q

from notifications.models import Notification, NotificationUser


def query_notifications(request):
    login_url = settings.LOGIN_URL + '?next=' + request.GET.get('path', '')
    if request.user.is_anonymous:
        return dict(authenticated=False, login_url=login_url)
    notifyes = list(
        Notification.objects.prefetch_related('notificationuser_set').filter(
            Q(to_all=True) | Q(notificationuser__user=request.user),
            active=True,
        ).exclude(excpt=request.user).distinct().order_by(
            '-datetime_creation'))  # TODO: фильтровать по разрешениям
    if not notifyes:
        has_notifyes = False
    else:
        has_notifyes = True
    new_notifyes: List[Notification] = []
    for notify in notifyes:  # type: Notification
        try:
            notification_user = notify.notificationuser_set.get(
                user=request.user)
            if notification_user.check_datetime is None:
                new_notifyes.append(notify)
        except NotificationUser.DoesNotExist:
            if notify.to_all:
                new_notifyes.append(notify)
    old_notifyes: List[Notification] = [x for x in notifyes if
                                        x not in new_notifyes]
    return dict(
        authenticated=True,
        has_notifications=has_notifyes,
        new_notifications=new_notifyes,
        old_notifications=old_notifyes,
        login_url=login_url,
    )
