import traceback

from django.core.exceptions import PermissionDenied
from django.http import Http404

from .models import ExceptionLog

class Log500ErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied)):
            return None

        exception_value = str(exception)
        exception_type = type(exception).__name__
        tb = exception.__traceback__
        exception_traceback = traceback.format_exception(
            type(exception), exception, tb
        )
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False):
            user = user
        else:
            user = None

        ExceptionLog.objects.create(
            path=request.path,
            value=exception_value,
            type=exception_type,
            traceback="\n".join(exception_traceback),
            user=user,
            request_params={'GET': dict(request.GET), 'POST': dict(request.POST)}
        )
        return None
