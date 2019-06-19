import json
from types import FunctionType

import requests
from django.conf import settings

from .models import Notification, NotificationUser

PUSH4SITE_DATA = dict(
    require=dict(Title='title',
                 Text='text',
                 ClickUrl='click_url',
                 ImageBase64='image.base64'),
    optional=dict(ButtonTexts=['text_1st_bt', 'text_2nd_bt'],
                  ButtonUrls=['url_1st_bt', 'url_2nd_bt']),
)

PUSH4SITE_RESPONSE = {
    'Success': 'success',
    'ErrorReason': 'error_description',
    'NotificationId': 'remote_id',
    'Status': 'status',
}

DEFAULT_CONFIG = {
    'URLS':{
        'SEND': 'https://push4site.com/interface/send',
        'SEND_PERSONAL': 'https://push4site.com/interface/personalNotification',
        'STATUS_PERSONAL': 'https://push4site.com/interface/personalNotificationStatus',
    },
    'KEY': '',
}


def get_config():
    user_config = getattr(settings, 'PUSH4SITE_CONFIG', {})

    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    return config


class Push4SiteException(Exception):
    pass


class Push4SiteAPI:
    _key = None

    def __init__(self, key:str = None):
        self._key = key

    def _request(self, url:str, method:FunctionType, data:dict):
        url = get_config()['URLS'][url]
        data.update({
            'ApiKey': self.key
        })
        r = method(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if r.status_code != 200:
            raise Push4SiteException('Bad Status Code: {code}'.format(code=r.status_code))

        return r

    @property
    def key(self):
        if not self._key:
            self._key = get_config()['KEY']
        return self._key

    def update_notificationuser_from_response(self, r:dict, n:NotificationUser):
        for k, v in PUSH4SITE_RESPONSE:
            if k in r.keys():
                setattr(n, v, r[k])
        n.save()

    def notify(self, notification:Notification):
        data = {}
        for key, value in PUSH4SITE_DATA['require'].items():
            data[key] = getattr(notification, value)
        for key, value in PUSH4SITE_DATA['optional'].items():
            data[key] = []
            for child_value in value:
                if getattr(notification, child_value) is not None:
                    data[key].append(getattr(notification, child_value))
        notificationuser_set = NotificationUser.objects.filter(notification=notification)
        if notificationuser_set.exists():
            url = 'SEND_PERSONAL'
            sample = data.copy()
            data = []
            for n_user in list(notificationuser_set):
                for sub_id in n_user.push4site:
                    data.append(sample.copy().update({'SubscriberId': sub_id}))
        else:
            url = 'SEND'
        if isinstance(data, list):
            for d in data:
                self.update_notification_from_response(self._request(
                    url, requests.post, d))
        else:
            self.update_notification_from_response(self._request(
                url, requests.post, data))
        return

    def get_status(self, n):
        return

