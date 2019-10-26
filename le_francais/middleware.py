from django.conf import settings
from django.middleware import csrf
from user_sessions.middleware import SessionMiddleware

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        super().process_request(request)
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        if request.META.get('HTTP_CLIENT_IP'):
            ip = request.META.get('HTTP_CLIENT_IP')
        elif request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
        elif request.META.get('HTTP_X_FORWARDED'):
            ip = request.META.get('HTTP_X_FORWARDED')
        elif request.META.get('HTTP_FORWARDED_FOR'):
            ip = request.META.get('HTTP_FORWARDED_FOR')
        elif request.META.get('HTTP_FORWARDED'):
            ip = request.META.get('HTTP_FORWARDED')
        elif request.META.get('REMOTE_ADDR'):
            ip = request.META.get('REMOTE_ADDR')
        else:
            ip = 'UNKNOWN'
        ip = ip.split(',')[0]
        request.session = engine.SessionStore(
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=session_key
        )
