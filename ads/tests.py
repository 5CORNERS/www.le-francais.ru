from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.sessions.middleware import SessionMiddleware
from ads.models import LineItem, Creative, Log
from ads.views import AdCounterRedirectView, get_creative_dict

User = get_user_model()

class LiveIncrementDecoupleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
        self.line_item = LineItem.objects.create(name='Test Line Item', priority=10)
        self.creative = Creative.objects.create(
            name='Test Creative',
            line_item=self.line_item,
            image_click_through_url='https://example.com',
            _width=300,
            _height=250
        )
        self.factory = RequestFactory()

    def test_live_view_does_not_increment_fields(self):
        # Initial views count
        initial_li_views = self.line_item.views
        initial_cr_views = self.creative.views

        # Simulate AJAX creative request
        request = self.factory.get('/ads/get-html/', {'ad_unit_name': 'test_unit'})
        request.user = self.user
        # Setup sessions
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.ip = '127.0.0.1'
        request.session['geoip'] = {'country_code': 'FR', 'city': 'Paris', 'country_name': 'France'}
        request.session.save()

        # Call the view logic
        res = get_creative_dict(request)

        # Verify a Log was created
        self.assertEqual(Log.objects.filter(creative=self.creative).count(), 1)

        # Reload models
        self.line_item.refresh_from_db()
        self.creative.refresh_from_db()

        # Verify that model views fields DID NOT change
        self.assertEqual(self.line_item.views, initial_li_views)
        self.assertEqual(self.creative.views, initial_cr_views)


from datetime import timedelta
from django.core.management import call_command

class CullLogsCommandTestCase(TestCase):
    def setUp(self):
        self.line_item = LineItem.objects.create(name='Cull Test Line Item', priority=1, views=10, clicks=5)
        self.creative = Creative.objects.create(
            name='Cull Test Creative',
            line_item=self.line_item,
            views=8,
            clicks=4,
            _width=300,
            _height=250
        )
        
        # Create logs using manual datetime manipulation (bypass auto_now_add via update where necessary, or just creating them normally)
        now = timezone.now()
        
        # Log 1: older than 10 days, clicked = True
        log1 = Log.objects.create(
            line_item=self.line_item,
            creative=self.creative,
            ip='127.0.0.1',
            clicked=True
        )
        Log.objects.filter(pk=log1.pk).update(datetime=now - timedelta(days=15))

        # Log 2: older than 10 days, clicked = False
        log2 = Log.objects.create(
            line_item=self.line_item,
            creative=self.creative,
            ip='127.0.0.1',
            clicked=False
        )
        Log.objects.filter(pk=log2.pk).update(datetime=now - timedelta(days=12))

        # Log 3: newer than 10 days (should NOT be culled), clicked = False
        log3 = Log.objects.create(
            line_item=self.line_item,
            creative=self.creative,
            ip='127.0.0.1',
            clicked=False
        )
        Log.objects.filter(pk=log3.pk).update(datetime=now - timedelta(days=5))

    def test_cull_logs_command(self):
        # Cull logs older than 10 days
        call_command('cull_logs', 10)

        # Reload models
        self.line_item.refresh_from_db()
        self.creative.refresh_from_db()

        # Expecting 2 culled logs: 2 views, 1 click added to model fields
        self.assertEqual(self.line_item.views, 12)  # 10 + 2
        self.assertEqual(self.line_item.clicks, 6)  # 5 + 1
        self.assertEqual(self.creative.views, 10)  # 8 + 2
        self.assertEqual(self.creative.clicks, 5)  # 4 + 1

        # Only 1 log (the newer one) should remain in the database
        self.assertEqual(Log.objects.count(), 1)


from ads.admin import LineItemAdmin, CreativeAdmin
from django.contrib.admin.sites import AdminSite

class AdminCombinedFieldsTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.line_item = LineItem.objects.create(name='Admin Test Line Item', views=100, clicks=10)
        self.creative = Creative.objects.create(
            name='Admin Test Creative',
            line_item=self.line_item,
            views=50,
            clicks=5,
            _width=300,
            _height=250
        )
        
        # Create active logs
        Log.objects.create(line_item=self.line_item, creative=self.creative, ip='127.0.0.1', clicked=True)
        Log.objects.create(line_item=self.line_item, creative=self.creative, ip='127.0.0.1', clicked=False)

    def test_admin_combined_fields(self):
        li_admin = LineItemAdmin(LineItem, self.site)
        cr_admin = CreativeAdmin(Creative, self.site)

        # LineItem combined counts:
        # Stored: views=100, clicks=10
        # Active logs: 2 views, 1 click
        self.assertEqual(li_admin.combined_views(self.line_item), 102)
        self.assertEqual(li_admin.combined_clicks(self.line_item), 11)

        # Creative combined counts:
        # Stored: views=50, clicks=5
        # Active logs: 2 views, 1 click
        self.assertEqual(cr_admin.combined_views(self.creative), 52)
        self.assertEqual(cr_admin.combined_clicks(self.creative), 6)


