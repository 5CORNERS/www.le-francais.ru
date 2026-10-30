from io import StringIO
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import Http404
from django.test import TestCase, RequestFactory, Client
from log_errors.models import ExceptionLog
from log_errors.middleware import Log500ErrorsMiddleware


class Log500ErrorsMiddlewareTestCase(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_social_auth_canceled_not_logged(self):
        """
        When a user cancels social OAuth (e.g. VK OAuth2),
        the request should redirect to login and should NOT be logged as a 500 error in ExceptionLog.
        """
        client = Client()
        before_count = ExceptionLog.objects.count()
        response = client.get(
            '/complete/vk-oauth2/?error=access_denied&error_reason=user_denied&error_description=User+denied+your+request&state=test',
            HTTP_HOST='www.le-francais.ru'
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/')
        after_count = ExceptionLog.objects.count()
        self.assertEqual(
            after_count, before_count,
            "AuthCanceled exception was logged to ExceptionLog, but it should have been caught and handled by SocialAuthExceptionMiddleware"
        )

    def test_http404_not_logged(self):
        """Http404 exceptions must not be logged as 500 errors."""
        req = self.rf.get('/some-nonexistent-path/')
        mw = Log500ErrorsMiddleware(lambda r: None)
        before_count = ExceptionLog.objects.count()
        mw.process_exception(req, Http404("Page not found"))
        self.assertEqual(ExceptionLog.objects.count(), before_count)

    def test_permission_denied_not_logged(self):
        """PermissionDenied exceptions must not be logged as 500 errors."""
        req = self.rf.get('/forbidden-path/')
        mw = Log500ErrorsMiddleware(lambda r: None)
        before_count = ExceptionLog.objects.count()
        mw.process_exception(req, PermissionDenied("Access denied"))
        self.assertEqual(ExceptionLog.objects.count(), before_count)

    def test_real_server_error_is_logged(self):
        """Actual unhandled exceptions must be logged to ExceptionLog."""
        req = self.rf.get('/some-path/')
        mw = Log500ErrorsMiddleware(lambda r: None)
        before_count = ExceptionLog.objects.count()
        try:
            raise ValueError("Something exploded")
        except ValueError as exc:
            mw.process_exception(req, exc)
        self.assertEqual(ExceptionLog.objects.count(), before_count + 1)
        last_log = ExceptionLog.objects.last()
        self.assertEqual(last_log.type, 'ValueError')
        self.assertEqual(last_log.value, 'Something exploded')

    def test_request_without_user_attribute_does_not_crash(self):
        """If request does not have user attribute, process_exception should not raise AttributeError."""
        req = self.rf.get('/some-path/')
        # req does not have user attribute by default on RequestFactory unless attached
        mw = Log500ErrorsMiddleware(lambda r: None)
        try:
            raise RuntimeError("Failure before auth middleware")
        except RuntimeError as exc:
            # Should not raise AttributeError: 'WSGIRequest' object has no attribute 'user'
            mw.process_exception(req, exc)
        last_log = ExceptionLog.objects.last()
        self.assertEqual(last_log.type, 'RuntimeError')
        self.assertIsNone(last_log.user)


class ClearExceptionLogsCommandTestCase(TestCase):
    def setUp(self):
        ExceptionLog.objects.create(type='Http404', value='Not found 1')
        ExceptionLog.objects.create(type='Http404', value='Not found 2')
        ExceptionLog.objects.create(type='Http404', value='Not found 3')
        ExceptionLog.objects.create(type='PermissionDenied', value='Denied 1')
        ExceptionLog.objects.create(type='ValueError', value='Server error')

    def test_clear_exception_logs_dry_run(self):
        out = StringIO()
        call_command('clear_exception_logs', dry_run=True, stdout=out)
        output = out.getvalue()
        self.assertIn('DRY RUN', output)
        self.assertIn('4', output)
        self.assertEqual(ExceptionLog.objects.count(), 5)

    def test_clear_exception_logs_default(self):
        out = StringIO()
        call_command('clear_exception_logs', batch_size=2, stdout=out)
        self.assertEqual(ExceptionLog.objects.count(), 1)
        remaining = ExceptionLog.objects.first()
        self.assertEqual(remaining.type, 'ValueError')

    def test_clear_exception_logs_custom_types(self):
        out = StringIO()
        call_command('clear_exception_logs', types='ValueError', stdout=out)
        self.assertEqual(ExceptionLog.objects.filter(type='ValueError').count(), 0)
        self.assertEqual(ExceptionLog.objects.filter(type='Http404').count(), 3)
