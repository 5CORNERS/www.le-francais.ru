import traceback

from .models import ExceptionLog

class Log500ErrorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        exception_value = str(exception)
        exception_type = type(exception).__name__
        tb = exception.__traceback__
        exception_traceback = traceback.format_exception(
            type(exception), exception, tb
        )
        ExceptionLog.objects.create(
            path=request.path,
            value=exception_value,
            type=exception_type,
            traceback="\n".join(exception_traceback),
            user=request.user if request.user.is_authenticated else None,
            request_params={'GET':dict(request.GET), 'POST':dict(request.POST)}
        )
        return None
