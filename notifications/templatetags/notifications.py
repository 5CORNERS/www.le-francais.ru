from typing import List

from django import template
from django.db.models import Q
from django.urls import reverse

from notifications.utils import query_notifications, blank_list
from ..models import NotificationUser, Notification
from django.conf import settings

register = template.Library()

@register.inclusion_tag('notifications/notifications.html', takes_context=True)
def notification_navbar_dropdown(context):
    return blank_list(context['request'])

@register.simple_tag()
def get_check_datetime(notification:Notification, user):
    try:
        return notification.notificationuser_set.get(user=user).check_datetime
    except NotificationUser.DoesNotExist:
        return None
