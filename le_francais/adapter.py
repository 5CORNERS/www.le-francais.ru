from allauth.account.adapter import DefaultAccountAdapter

from django.conf import settings

class AccountAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        allowed_hosts = ['courses.le-francais.ru', 'www.le-francais.ru', 'video.le-francais.ru']
        if settings.DEBUG:
            allowed_hosts += ['localhost', '127.0.0.1', 'localhost:8080', 'localhost:8081']
        return is_safe_url(url, allowed_hosts=allowed_hosts)