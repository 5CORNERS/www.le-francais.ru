from django.conf import settings


class YandexAPI:
    _client = None
    _api_key = None

    @property
    def api_key(self):
        if not self._api_key:
            self._api_key = settings.YANDEX_CLOUD_KEY
        return self._api_key

    @property
    def client(self):
