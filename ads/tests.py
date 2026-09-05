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
