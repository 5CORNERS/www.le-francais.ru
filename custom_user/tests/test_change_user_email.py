import io
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

class ChangeUserEmailCommandTestCase(TestCase):
    def setUp(self):
        # Create users with unique fields
        self.user1 = User.objects.create_user(
            username='cmdtestuser1', 
            email='cmduser1@example.com', 
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='cmdtestuser2', 
            email='cmduser2@example.com', 
            password='password2'
        )
        # Create corresponding allauth EmailAddress records
        EmailAddress.objects.create(user=self.user1, email='cmduser1@example.com', verified=True, primary=True)
        EmailAddress.objects.create(user=self.user2, email='cmduser2@example.com', verified=True, primary=True)

    def test_change_email_success(self):
        out = io.StringIO()
        call_command('change_user_email', 'cmdtestuser1', 'cmdnew_email@example.com', '--no-input', stdout=out)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'cmdnew_email@example.com')
        self.assertTrue(EmailAddress.objects.filter(user=self.user1, email='cmdnew_email@example.com', verified=True, primary=True).exists())
        self.assertFalse(EmailAddress.objects.filter(user=self.user1, email='cmduser1@example.com').exists())

    def test_change_email_lookup_by_id(self):
        out = io.StringIO()
        call_command('change_user_email', str(self.user1.id), 'cmdnew_by_id@example.com', '--no-input', stdout=out)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'cmdnew_by_id@example.com')

    def test_change_email_already_taken(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit):
            call_command('change_user_email', 'cmdtestuser1', 'cmduser2@example.com', '--no-input', stdout=out)
