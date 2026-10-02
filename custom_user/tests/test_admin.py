from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from social_django.models import UserSocialAuth
from custom_user.admin import CustomUserAdmin, EmailStatusFilter

User = get_user_model()


class CustomUserAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        self.rf = RequestFactory()

    def test_list_display_includes_email_status(self):
        self.assertIn('email_status', self.admin.list_display)
        email_idx = self.admin.list_display.index('email')
        status_idx = self.admin.list_display.index('email_status')
        self.assertEqual(status_idx, email_idx + 1)

    def test_email_status_oauth_user(self):
        user = User.objects.create_user(username='u_oauth', email='u_oauth@example.com', password='pw')
        UserSocialAuth.objects.create(user=user, provider='google', uid='12345')
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        status_html = self.admin.email_status(user)
        self.assertIn('OAuth', status_html)
        self.assertIn('google', status_html)

    def test_email_status_verified_user(self):
        user = User.objects.create_user(username='u_verified', email='u_verified@example.com', password='pw')
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)

        status_html = self.admin.email_status(user)
        self.assertIn('Verified', status_html)
        self.assertNotIn('OAuth', status_html)

    def test_email_status_unverified_user(self):
        user = User.objects.create_user(username='u_unverified', email='u_unverified@example.com', password='pw')
        EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)

        status_html = self.admin.email_status(user)
        self.assertIn('Unverified', status_html)

    def test_email_status_no_email_record(self):
        user = User.objects.create_user(username='u_norec', email='u_norec@example.com', password='pw')
        status_html = self.admin.email_status(user)
        self.assertIn('Unverified', status_html)

    def test_get_queryset_prefetches_relations(self):
        request = self.rf.get('/admin/custom_user/user/')
        qs = self.admin.get_queryset(request)
        self.assertIn('emailaddress_set', qs._prefetch_related_lookups)
        self.assertIn('social_auth', qs._prefetch_related_lookups)

    def test_filter_oauth_users(self):
        u1 = User.objects.create_user(username='u1_oauth', email='u1@example.com', password='pw')
        UserSocialAuth.objects.create(user=u1, provider='vk-oauth2', uid='999')
        u2 = User.objects.create_user(username='u2_ver', email='u2@example.com', password='pw')
        EmailAddress.objects.create(user=u2, email=u2.email, verified=True, primary=True)
        u3 = User.objects.create_user(username='u3_unver', email='u3@example.com', password='pw')

        f = EmailStatusFilter(None, {'email_status': 'oauth'}, User, self.admin)
        qs = f.queryset(None, User.objects.all())
        self.assertIn(u1, qs)
        self.assertNotIn(u2, qs)
        self.assertNotIn(u3, qs)

        f_ver = EmailStatusFilter(None, {'email_status': 'verified'}, User, self.admin)
        qs_ver = f_ver.queryset(None, User.objects.all())
        self.assertIn(u2, qs_ver)
        self.assertNotIn(u1, qs_ver)
        self.assertNotIn(u3, qs_ver)

        f_unver = EmailStatusFilter(None, {'email_status': 'unverified'}, User, self.admin)
        qs_unver = f_unver.queryset(None, User.objects.all())
        self.assertIn(u3, qs_unver)
        self.assertNotIn(u1, qs_unver)
        self.assertNotIn(u2, qs_unver)
