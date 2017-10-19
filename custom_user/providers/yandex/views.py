from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import YandexProvider

import requests


class YandexOAuth2Adapter(OAuth2Adapter):
    provider_id = YandexProvider.id
    access_token_url = 'https://oauth.yandex.com/token'
    authorize_url = 'https://oauth.yandex.com/authorize'
    profile_url = 'http://passport.yandex.ru/profile'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'client_id': token.token})
        extra_data = resp.json()
        if app_settings.QUERY_EMAIL and not extra_data.get('email'):
            extra_data['email'] = self.get_email(token)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(YandexOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(YandexOAuth2Adapter)
