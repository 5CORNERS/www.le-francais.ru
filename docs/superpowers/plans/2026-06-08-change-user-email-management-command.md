# change_user_email Management Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a robust and safe Django management command `change_user_email` to change, verify, and set a user's primary email address under django-allauth while purging old emails.

**Architecture:** Implement a Django management command extending `BaseCommand` in `custom_user/management/commands/change_user_email.py`. It uses `transaction.atomic` for database safety and prompts for user confirmation unless `--no-input` is passed.

**Tech Stack:** Django (>=1.11.29), django-allauth (0.37.0), Python 3.7

---

### File Structure Map

- **Modified Files**:
  - `custom_user/tests.py`: Append tests to verify command execution, lookup, validation, transactions, and old email deletion.
- **New Files**:
  - `custom_user/management/commands/change_user_email.py`: The management command file containing lookups, confirmations, and transactions.

---

### Task 1: Append Failing Tests

**Files:**
- Modify: `custom_user/tests.py`

- [ ] **Step 1: Append failing tests for `change_user_email`**

Add the test class `ChangeUserEmailCommandTestCase` to the end of `custom_user/tests.py`:

```python
import io
from django.core.management import call_command
from allauth.account.models import EmailAddress

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run the following shell command to run the newly added tests:
Run: `python manage.py test custom_user.tests.ChangeUserEmailCommandTestCase`
Expected Output: Failures with `CommandError: Unknown command: 'change_user_email'` or similar lookup errors.

- [ ] **Step 3: Commit changes**

```powershell
git add custom_user/tests.py
git commit -m "test: add failing tests for change_user_email management command"
```

---

### Task 2: Implement `change_user_email` Management Command

**Files:**
- Create: `custom_user/management/commands/change_user_email.py`

- [ ] **Step 1: Write the command code**

Create `custom_user/management/commands/change_user_email.py` and populate it with the following code:

```python
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

class Command(BaseCommand):
    help = 'Changes a user\'s email, marks it as verified, sets it as primary, and deletes other old emails'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_identifier',
            type=str,
            help='Username, email, or user ID of the target user'
        )
        parser.add_argument(
            'new_email',
            type=str,
            help='The new email address'
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            dest='no_input',
            default=False,
            help='Do not prompt for interactive confirmation'
        )

    def handle(self, *args, **options):
        user_identifier = options['user_identifier']
        new_email = options['new_email'].strip().lower()
        no_input = options['no_input']

        User = get_user_model()
        user = None

        # 1. Resolve user
        if user_identifier.isdigit():
            user = User.objects.filter(pk=int(user_identifier)).first()
        
        if not user:
            user = User.objects.filter(username__iexact=user_identifier).first()
            
        if not user:
            user = User.objects.filter(email__iexact=user_identifier).first()

        if not user:
            self.stderr.write(self.style.ERROR(f"No user found with identifier '{user_identifier}'."))
            sys.exit(1)

        # 2. Check if new email is already primary/matching
        if user.email.lower() == new_email:
            self.stdout.write(self.style.SUCCESS(f"User email is already '{new_email}'. No action needed."))
            return

        # 3. Check for duplicates/email conflicts
        other_email_exists = EmailAddress.objects.filter(email__iexact=new_email).exclude(user=user).exists()
        if other_email_exists:
            self.stderr.write(self.style.ERROR(f"The email '{new_email}' is already registered to another user."))
            sys.exit(1)

        # 4. Interactive Confirmation
        if not no_input:
            self.stdout.write(self.style.WARNING(f"\nAbout to change email for:\n  User: {user.username} (ID: {user.pk})\n  Current Primary: {user.email}\n  New Primary: {new_email}\n"))
            self.stdout.write(self.style.WARNING("This will mark the new email verified, set it primary, and delete the user's old email addresses."))
            response = input("Are you sure you want to proceed? [y/N]: ").strip().lower()
            if response not in ('y', 'yes'):
                self.stdout.write("Operation cancelled.")
                return

        # 5. Database Transaction Swap
        try:
            with transaction.atomic():
                # Identify old emails to delete
                old_emails = list(EmailAddress.objects.filter(user=user).exclude(email__iexact=new_email))

                # Create/Get new email Address record
                new_email_obj, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=new_email
                )
                
                new_email_obj.verified = True
                new_email_obj.save()

                # Set new email as primary (calls allauth set_as_primary logic)
                new_email_obj.set_as_primary()

                # Delete all old EmailAddress records for this user
                deleted_emails = []
                for old_email in old_emails:
                    deleted_emails.append(old_email.email)
                    old_email.delete()

                self.stdout.write(self.style.SUCCESS(f"Successfully changed primary email to {new_email} for user {user.username}."))
                if deleted_emails:
                    self.stdout.write(self.style.SUCCESS(f"Deleted old email address(es): {', '.join(deleted_emails)}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Database transaction failed: {e}"))
            sys.exit(1)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `python manage.py test custom_user.tests.ChangeUserEmailCommandTestCase`
Expected Output: All tests pass.

- [ ] **Step 3: Commit changes**

```powershell
git add custom_user/management/commands/change_user_email.py
git commit -m "feat: implement change_user_email management command with transactions"
```
