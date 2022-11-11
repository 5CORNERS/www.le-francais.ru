import datetime

import geoip2.errors
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.middleware import csrf
from django.utils import timezone
from django_session_header.middleware import SessionHeaderMixin
from user_sessions.middleware import SessionMiddleware

from home.consts import IP_HEADERS_LIST

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
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
        elif request.META.get('REMOTE_ADDR'):
            ip = request.META.get('REMOTE_ADDR')
        elif request.META.get('HTTP_X_FORWARDED'):
            ip = request.META.get('HTTP_X_FORWARDED')
        elif request.META.get('HTTP_CLIENT_IP'):
            ip = request.META.get('HTTP_CLIENT_IP')
        elif request.META.get('HTTP_FORWARDED_FOR'):
            ip = request.META.get('HTTP_FORWARDED_FOR')
        elif request.META.get('HTTP_FORWARDED'):
            ip = request.META.get('HTTP_FORWARDED')
        else:
            ip = 'UNKNOWN'
        ip = ip.split(',')[0]
        request.session = engine.SessionStore(
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=session_key
        )
        request.session['request_ips'] = {k:request.META.get(k, '') for k in IP_HEADERS_LIST}


class GeoIpSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # This product includes GeoLite2 data created by MaxMind, available from
        # https://www.maxmind.com
        now = timezone.now()
        ip = request.session.ip
        try:
            if 'geoip' in request.session and 'country_code' in request.session['geoip']:
                geoip_dict = request.session['geoip']
                last_check = datetime.datetime.fromisoformat(
                    geoip_dict['last_check'])
                if (now - last_check).days > 1:
                    g = GeoIP2()
                    geoip_dict['last_check'] = now.isoformat()
                    for k, v in g.city(ip).items():
                        geoip_dict[k] = v
                    request.session['geoip'] = geoip_dict
            else:
                g = GeoIP2()
                geoip_dict = {
                    'last_check': now.isoformat()
                }
                for k, v in g.city(ip).items():
                    geoip_dict[k] = v
                request.session['geoip'] = geoip_dict

            user = request.user
            if user.is_authenticated and (
            user.country_code, user.city, user.region) != (
            geoip_dict['country_code'], geoip_dict['city'],
            geoip_dict['region']):
                user.country_code = geoip_dict['country_code']
                user.city = geoip_dict['city']
                user.country_name = geoip_dict['country_name']
                user.region = geoip_dict['region']
                user.save(update_fields=['country_code','city','country_name','region'])
        except geoip2.errors.AddressNotFoundError:
            geoip_dict = {
                'last_check': now.isoformat()
            }
            request.session['geoip'] = geoip_dict
