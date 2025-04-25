import json
from io import BytesIO

from django.conf import settings
from requests import request


class YandexAPI:
    _client = None
    _api_key = None

    @property
    def api_key(self):
        if not self._api_key:
            self._api_key = settings.YANDEX_CLOUD_KEY
        return self._api_key

    def get_audio_stream(self, speechkit_task):
        response = request(
            method='POST',
            url='https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
            headers={'Authorization': f"Api-Key {self.api_key}"},
            data=speechkit_task.to_dict()
        )
        if response.status_code == 200:
            stream = BytesIO()
            for chunk in response.iter_content(chunk_size=None):
                stream.write(chunk)
            stream.seek(0)
            return stream, False, 'TTS_DONE', None
        else:
            data = json.loads(response.text)
            return None, True, 'TTS_ERROR', data['error_message']
