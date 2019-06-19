from django import template
from django.urls import reverse

from ..models import NotificationUser
from django.conf import settings

register = template.Library()

@register.inclusion_tag('notifications/notifications.html', takes_context=True)
def notification_navbar_dropdown(context):
    request = context['request']
    check_list_url = reverse('notifications:check_list')
    login_url = settings.LOGIN_URL + '?next={path}'.format(path=request.path)
    if request.user.is_anonymous:
        return dict(authenticated=False, login_url=login_url)
    notifyes = list(NotificationUser.objects.select_related('notification').filter(
        user=request.user, notification__active=True).order_by('-notification__datetime_creation'))
    if not notifyes:
        has_notifyes = False
    else:
        has_notifyes = True
    new_notifyes = list(filter(lambda x: x.check_datetime is None, notifyes))
    old_notifyes = [x for x in notifyes if x not in new_notifyes]
    return dict(old_notifications=old_notifyes, new_notifications=new_notifyes, check_list_url=check_list_url, has_notifications=has_notifyes, authenticated=True)
