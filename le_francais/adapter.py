from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        return is_safe_url(url, allowed_hosts=['courses.le-francais.ru', 'www.le-francais.ru', 'video.le-francais.ru'])