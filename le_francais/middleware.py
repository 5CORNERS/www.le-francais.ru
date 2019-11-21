from django.conf import settings
from django.middleware import csrf
from django_session_header.middleware import SessionHeaderMixin
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

# This code is from
# https://github.com/ryanhiebert/django-session-header


class SessionHeaderMiddleware(SessionMiddleware):
    def __init__(self, get_response=None):
        engine = import_module(settings.SESSION_ENGINE)
        super(SessionMiddleware, self).__init__(get_response)
        bases = (SessionHeaderMixin, engine.SessionStore)
        self.SessionStore = type('SessionStore', bases, {})

    def process_request(self, request):
        super().process_request(request)
        sessionid = request.META.get(u'HTTP_X_SESSIONID')
        if sessionid:
            request.session = self.SessionStore(sessionid)
            request.session.csrf_exempt = True

    def process_response(self, request, response):
        supr = super()
        response = supr.process_response(request, response)
        if request.session.session_key:
            response['X-SessionID'] = request.session.session_key
        return response


class SessionHeaderMixin(object):
    def __init__(self, session_key=None):
        super(SessionHeaderMixin, self).__init__(session_key)
        self.csrf_exempt = False


class CsrfViewMiddleware(csrf.CsrfViewMiddleware):
    def process_view(self, request, *args, **kwargs):
        if not request.session.csrf_exempt:
            supr = super(CsrfViewMiddleware, self)
            return supr.process_view(request, *args, **kwargs)


class CustomSessionMiddleware(SessionHeaderMiddleware):
    def process_request(self, request):
        super(SessionHeaderMiddleware, self).process_request(request)
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
