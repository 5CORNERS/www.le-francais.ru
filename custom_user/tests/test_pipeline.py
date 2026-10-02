from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from custom_user.pipeline import create_allauth_email

User = get_user_model()


class CreateAllauthEmailPipelineTests(TestCase):
    def test_creates_verified_email_for_new_user(self):
        user = User.objects.create_user(username='oauthnew', email='oauthnew@example.com', password='pw')
        create_allauth_email(backend=None, user=user, response={})
        ea = EmailAddress.objects.filter(user=user, email=user.email).first()
        self.assertIsNotNone(ea)
        self.assertTrue(ea.verified)
        self.assertTrue(ea.primary)

    def test_updates_existing_unverified_email_to_verified(self):
        user = User.objects.create_user(username='oauthexisting', email='oauthexisting@example.com', password='pw')
        ea = EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
        create_allauth_email(backend=None, user=user, response={})
        ea.refresh_from_db()
        self.assertTrue(ea.verified)
