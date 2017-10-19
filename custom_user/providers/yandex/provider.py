from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class YandexAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('profileUrl')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar')

    def to_str(self):
        dflt = super(YandexAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)


class YandexProvider(OAuth2Provider):
    id = 'yandex'
    name = 'Yandex'
    account_class = YandexAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(username=data.get('username'),
                    name=data.get('displayName'),
                    email=data.get('email'))


provider_classes = [YandexProvider]
