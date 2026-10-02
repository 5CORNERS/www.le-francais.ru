from allauth.account.adapter import DefaultAccountAdapter

from django.conf import settings

class AccountAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        allowed_hosts = ['courses.le-francais.ru', 'www.le-francais.ru', 'video.le-francais.ru']
        if settings.DEBUG:
            allowed_hosts += ['localhost', '127.0.0.1', 'localhost:8080', 'localhost:8081']
        return is_safe_url(url, allowed_hosts=allowed_hosts)

    def unstash_verified_email(self, request):
        if not request or not hasattr(request, 'session'):
            return None
        return super(AccountAdapter, self).unstash_verified_email(request)

    def is_email_verified(self, request, email):
        if not request or not hasattr(request, 'session'):
            return False
        return super(AccountAdapter, self).is_email_verified(request, email)

    def stash_user(self, request, user):
        if not request or not hasattr(request, 'session'):
            return None
        return super(AccountAdapter, self).stash_user(request, user)

    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        try:
            super(AccountAdapter, self).add_message(
                request, level, message_template,
                message_context=message_context, extra_tags=extra_tags
            )
        except Exception:
            pass